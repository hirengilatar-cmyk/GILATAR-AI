from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
from ddgs import DDGS
from urllib.request import Request, urlopen
from urllib.parse import urlencode
from html.parser import HTMLParser
import xml.etree.ElementTree as ET
import json
import random
import re

app = Flask(__name__)

# =========================
# GILATAR AI 15.0 BRAIN
# =========================

GUJARATI_TO_ENGLISH = {
    "ભારતના": "India", "ભારતમાં": "India", "ભારત": "India",
    "વડાપ્રધાન": "Prime Minister", "પ્રધાનમંત્રી": "Prime Minister",
    "રાજધાની": "capital", "પાટનગર": "capital",
    "ગુજરાતના": "Gujarat", "ગુજરાતની": "Gujarat", "ગુજરાતનું": "Gujarat",
    "ગુજરાતમાં": "Gujarat", "ગુજરાત": "Gujarat",
    "રાજકોટમાં": "Rajkot", "રાજકોટ": "Rajkot",
    "અમદાવાદમાં": "Ahmedabad", "અમદાવાદ": "Ahmedabad",
    "મુખ્યમંત્રી": "Chief Minister", "રાષ્ટ્રપતિ": "President",
    "હવામાન": "weather", "તાપમાન": "temperature",
    "સમાચાર": "latest news", "ક્રિકેટ": "cricket",
    "વિજ્ઞાન": "science", "ટેકનોલોજી": "technology",
    "કમ્પ્યુટર": "computer", "મોબાઇલ": "mobile phone",
    "ઇતિહાસ": "history", "શિક્ષણ": "education",
    "ભાવ": "price", "કિંમત": "price",
    "આજે": "today", "કાલે": "tomorrow",
    "કોણ": "", "શું": "", "ક્યાં": "", "ક્યારે": "",
    "કઈ": "", "કયો": "", "કયું": "", "છે": "",
    "કેમ": "", "વિશે": "", "મને": "", "જણાવો": "",
    "કહો": "", "કેટલો": "", "કેટલી": "", "કેટલા": "",
    "અને": "", "ના": "", "ની": "", "નું": "", "નો": ""
}


def make_search_query(question):
    """Convert common Gujarati terms into English search keywords."""
    if not any("\u0A80" <= ch <= "\u0AFF" for ch in question):
        return question.strip()
    converted = question
    for gujarati in sorted(GUJARATI_TO_ENGLISH, key=len, reverse=True):
        converted = converted.replace(gujarati, " " + GUJARATI_TO_ENGLISH[gujarati] + " ")
    words = re.findall(r"[A-Za-z0-9]+", converted)
    # Remove duplicates while keeping the original word order.
    return " ".join(dict.fromkeys(words)).strip()


class SearchHTMLParser(HTMLParser):
    """Small parser for search-result title/link/snippet blocks."""
    def __init__(self):
        super().__init__()
        self.results = []
        self.current = None
        self.capture = None
        self.depth = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = attrs.get("class", "")
        if tag == "a" and ("result__a" in classes or "b_algo" in classes):
            if self.current and self.current.get("title"):
                self.results.append(self.current)
            self.current = {"title": "", "href": attrs.get("href", ""), "body": ""}
            self.capture = "title"
        elif self.current and tag in ("div", "a") and ("result__snippet" in classes or "b_caption" in classes):
            self.capture = "body"

    def handle_data(self, data):
        if self.current and self.capture:
            self.current[self.capture] += data

    def handle_endtag(self, tag):
        if self.capture == "title" and tag == "a":
            self.capture = None
        elif self.capture == "body" and tag == "div":
            self.capture = None

    def close(self):
        super().close()
        if self.current and self.current.get("title"):
            self.results.append(self.current)


def fetch_url(url, timeout=6):
    req = Request(url, headers={"User-Agent": "Mozilla/5.0 (compatible; GILATARAI/15.0)"})
    with urlopen(req, timeout=timeout) as response:
        return response.read().decode("utf-8", errors="replace")


def search_bing_rss(query):
    url = "https://www.bing.com/search?" + urlencode({"q": query, "format": "rss"})
    raw = fetch_url(url, timeout=6)
    root = ET.fromstring(raw)
    results = []
    for item in root.findall(".//item")[:5]:
        results.append({
            "title": item.findtext("title", default="Search result"),
            "href": item.findtext("link", default=""),
            "body": item.findtext("description", default="")
        })
    return results


def search_duckduckgo_html(query):
    url = "https://html.duckduckgo.com/html/?" + urlencode({"q": query, "kl": "in-en"})
    parser = SearchHTMLParser()
    parser.feed(fetch_url(url, timeout=6))
    return [r for r in parser.results if r.get("href")][:5]


def search_wikipedia(query):
    """A lightweight fallback for encyclopedia-style questions."""
    api = "https://en.wikipedia.org/w/api.php?" + urlencode({
        "action": "query", "list": "search", "srsearch": query,
        "format": "json", "utf8": 1
    })
    data = json.loads(fetch_url(api, timeout=6))
    results = []
    for item in data.get("query", {}).get("search", [])[:5]:
        title = item.get("title", "")
        page = "https://en.wikipedia.org/wiki/" + title.replace(" ", "_")
        snippet = re.sub(r"<.*?>", "", item.get("snippet", ""))
        results.append({"title": title, "href": page, "body": snippet})
    return results


def concise_gujarati_answer(question, results):
    low = question.lower()

    # Stable common fact; link to the Government of Gujarat portal.
    if "ગુજરાત" in low and any(x in low for x in ["રાજધાની", "પાટનગર"]):
        return ("જવાબ: ગુજરાતની રાજધાની ગાંધીનગર છે. 💜\n"
                "સ્રોત: https://gujaratindia.gov.in/")

    # Keep the current office-holder answer clean and attach a result source.
    if any(term in low for term in ["વડાપ્રધાન", "પ્રધાનમંત્રી", "prime minister"]):
        for item in results:
            body = item.get("body", "")
            combined = item.get("title", "") + " " + body
            if "Narendra Modi" in combined and ("current prime minister" in body.lower() or "prime minister of india" in item.get("title", "").lower()):
                return ("જવાબ: ભારતના વર્તમાન વડાપ્રધાન નરેન્દ્ર મોદી છે. 💜\n"
                        f"સ્રોત: {item.get('href', '')}")

    answer = "🌐 ઇન્ટરનેટ સર્ચનો ટૂંકો સાર:\n\n"
    shown = 0
    for item in results:
        title = re.sub(r"\s+", " ", (item.get("title") or "માહિતી")).strip()
        body = re.sub(r"\s+", " ", (item.get("body") or "")).strip()
        url = (item.get("href") or "").strip()
        if not title and not body and not url:
            continue
        shown += 1
        answer += f"{shown}. {title}\n"
        if body:
            snippet = body[:220].rsplit(" ", 1)[0] + ("…" if len(body) > 220 else "")
            answer += f"માહિતી: {snippet}\n"
        if url:
            answer += f"સ્રોત: {url}\n"
        answer += "\n"
        if shown >= 3:
            break
    return answer if shown else None


def internet_search(question):
    search_question = make_search_query(question)
    if not search_question:
        return None

    # Try independent search routes so one provider timeout does not end the search.
    providers = [
        ("Bing RSS", search_bing_rss),
        ("DuckDuckGo HTML", search_duckduckgo_html),
        ("Wikipedia", search_wikipedia),
    ]
    for provider_name, provider in providers:
        try:
            print(f"Internet Search Provider: {provider_name} | Query: {search_question}")
            results = provider(search_question)
            if results:
                answer = concise_gujarati_answer(question, results)
                if answer:
                    return answer
        except Exception as e:
            print(f"{provider_name} Search Error: {e}")

    # Last fallback: DDGS. Its provider network can occasionally time out.
    try:
        print("Internet Search Provider: DDGS | Query:", search_question)
        results = DDGS(timeout=5).text(search_question, region="in-en", max_results=5)
        if results:
            return concise_gujarati_answer(question, results)
    except Exception as e:
        print("DDGS Search Error:", str(e))
    return None


def brain(q):
    q = q.strip()
    if not q:
        return "કૃપા કરીને કંઈક લખો. 😊"
    low = q.lower()

    if any(x in low for x in ["hello", "hi", "નમસ્તે", "હેલો"]):
        return "નમસ્તે! 💜 હું GILATAR AI 15.0 છું. તમારી મદદ માટે તૈયાર છું!"
    if "તમારું નામ" in low or "your name" in low:
        return "મારું નામ GILATAR AI 15.0 છે. 💜"
    if "કેમ છો" in low or "how are you" in low:
        return "હું એકદમ સરસ છું! તમે કેમ છો? 😊"
    if "સમય" in low or "time" in low:
        return "હાલનો સમય: " + datetime.now().strftime("%I:%M %p")
    if "તારીખ" in low or "date" in low:
        return "આજની તારીખ: " + datetime.now().strftime("%d-%m-%Y")
    if "જોક" in low or "joke" in low:
        return random.choice([
            "શિક્ષક: હોમવર્ક ક્યાં છે? વિદ્યાર્થી: સર, ઘરે જ છે! 😂",
            "કમ્પ્યુટર કેમ ઠંડું રહે છે? કારણ કે તેની પાસે Windows છે! 😄",
            "મોબાઇલ બોલ્યો: મને ચાર્જ કરો, હું પણ થાકી ગયો છું! 😂"
        ])
    if "આભાર" in low or "thank" in low:
        return "તમારું સ્વાગત છે! 💜"
    if "બાય" in low or "bye" in low:
        return "આવજો! ફરી મળીએ. 💜"
    if "મદદ" in low or "help" in low:
        return ("હું તમારી મદદ કરી શકું છું:\n"
                "• સમય અને તારીખ\n• સામાન્ય પ્રશ્નો\n• જોક્સ\n"
                "• ગુજરાતી keyword આધારિત ઇન્ટરનેટ સર્ચ\n")

    result = internet_search(q)
    if result:
        return result
    return ("માફ કરશો! અત્યારે ઉપલબ્ધ સર્ચ સેવાઓમાંથી પરિણામ મળ્યું નથી. 💜\n"
            "થોડી વાર પછી ફરી પ્રયાસ કરો અથવા પ્રશ્નના મુખ્ય શબ્દો English માં લખો.")


# =========================
# FUTURISTIC HOLOGRAM UI
# =========================

HTML = r"""
<!DOCTYPE html>
<html lang="gu">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>GILATAR AI 15.0</title>

<style>
* { box-sizing: border-box; }

body {
    margin: 0;
    min-height: 100vh;
    background: radial-gradient(ellipse at 50% 35%,
    #35105c 0%, #10051e 45%, #03020b 100%);
    color: #ead5ff;
    font-family: Arial, sans-serif;
    overflow-x: hidden;
}

body::before {
    content: "";
    position: fixed;
    inset: 0;
    pointer-events: none;
    background-image:
        linear-gradient(#bd66ff0b 1px, transparent 1px),
        linear-gradient(90deg, #bd66ff0b 1px, transparent 1px);
    background-size: 35px 35px;
}

header {
    text-align: center;
    padding: 22px 10px 5px;
}

.logo {
    font-size: 28px;
    font-weight: 900;
    letter-spacing: 3px;
    color: #e9c8ff;
    text-shadow: 0 0 8px #c56aff, 0 0 22px #a020f0;
}

.version {
    color: #bd83ff;
    font-size: 11px;
    letter-spacing: 5px;
    margin-top: 8px;
}

.status {
    color: #cda7ff;
    font-size: 12px;
    margin-top: 15px;
}

.reactor-area {
    height: 250px;
    display: flex;
    align-items: center;
    justify-content: center;
    position: relative;
}

.ring {
    position: absolute;
    width: 205px;
    height: 205px;
    border: 2px solid #a832ff;
    border-radius: 50%;
    box-shadow: 0 0 15px #a832ff, inset 0 0 15px #a832ff;
    animation: rotate 10s linear infinite;
}

.ring.two {
    width: 175px;
    height: 175px;
    border-style: dashed;
    border-color: #e0aaff;
    animation: rotateBack 8s linear infinite;
}

.ring.three {
    width: 235px;
    height: 235px;
    border-color: #7132b5;
    border-style: dotted;
    animation: rotate 18s linear infinite;
}

.core {
    width: 115px;
    height: 115px;
    border-radius: 50%;
    background: radial-gradient(circle,
    #f4d9ff 0%, #c65aff 20%, #7217c7 55%, #180526 100%);
    box-shadow: 0 0 20px #bc52ff, 0 0 55px #9c27ff,
    0 0 90px #7b20c7;
    display: flex;
    align-items: center;
    justify-content: center;
    color: white;
    font-size: 15px;
    font-weight: bold;
    text-align: center;
    animation: pulse 2s ease-in-out infinite;
}

@keyframes rotate {
    from { transform: rotate(0deg); }
    to { transform: rotate(360deg); }
}

@keyframes rotateBack {
    from { transform: rotate(360deg); }
    to { transform: rotate(0deg); }
}

@keyframes pulse {
    0%, 100% { transform: scale(1); filter: brightness(1); }
    50% { transform: scale(1.08); filter: brightness(1.4); }
}

.clock {
    text-align: center;
    color: #e7c8ff;
    font-size: 18px;
    letter-spacing: 2px;
    margin-bottom: 18px;
}

.panel {
    max-width: 720px;
    width: 94%;
    margin: auto;
    padding: 15px;
    border: 1px solid #9c42d9;
    border-radius: 18px;
    background: #160b28d9;
    box-shadow: 0 0 25px #8b20c544;
}

.chat {
    height: 300px;
    overflow-y: auto;
    padding: 10px;
    text-align: left;
    border-radius: 12px;
    background: #090515;
    border: 1px solid #4d2471;
}

.message {
    padding: 12px;
    margin: 9px 0;
    border-radius: 12px;
    white-space: pre-wrap;
    line-height: 1.6;
    font-size: 14px;
    overflow-wrap: anywhere;
}

.bot {
    background: #29113e;
    border-left: 3px solid #c45aff;
    color: #f1dfff;
}

.user {
    background: #45166b;
    border-right: 3px solid #e4aaff;
    color: white;
    text-align: right;
}

.input-area {
    display: flex;
    gap: 8px;
    margin-top: 13px;
}

input {
    min-width: 0;
    flex: 1;
    padding: 14px;
    background: #0c0617;
    border: 1px solid #a34be2;
    border-radius: 12px;
    color: white;
    outline: none;
    font-size: 15px;
}

input:focus { box-shadow: 0 0 12px #a832ff; }

button {
    padding: 12px 15px;
    border: 1px solid #c36aff;
    border-radius: 10px;
    background: linear-gradient(135deg, #60208b, #260b40);
    color: white;
    font-weight: bold;
    cursor: pointer;
}

button:active {
    transform: scale(.95);
    background: #a832ff;
}

.send {
    background: linear-gradient(135deg, #a832ff, #6013a0);
}

.buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
    margin-top: 13px;
}

.buttons button { flex: 1 1 120px; }

.footer {
    text-align: center;
    padding: 22px 10px;
    color: #a879c9;
    font-size: 11px;
    letter-spacing: 2px;
}

@media(max-width: 480px) {
    .logo { font-size: 23px; }
    .reactor-area { height: 230px; }
    .ring.three { width: 215px; height: 215px; }
    .chat { height: 280px; }
    button { padding: 12px 10px; }
}
</style>
</head>

<body>

<header>
    <div class="logo">GILATAR AI</div>
    <div class="version">15.0 SMART INTERNET SEARCH</div>
    <div class="status">● SYSTEM ONLINE</div>
</header>

<div class="reactor-area">
    <div class="ring three"></div>
    <div class="ring"></div>
    <div class="ring two"></div>
    <div class="core">GILATAR<br>AI 15.0</div>
</div>

<div class="clock" id="clock">00:00:00</div>

<div class="panel">
    <div class="chat" id="chat">
        <div class="message bot">
            GILATAR: નમસ્તે! 💜
            હું GILATAR AI 15.0 છું.
            હવે હું ટૂંકા જવાબ અને સર્ચના સ્રોત બતાવું છું!
        </div>
    </div>

    <div class="input-area">
        <input id="msg" placeholder="તમારો પ્રશ્ન લખો..."
        onkeydown="if(event.key==='Enter') ask()">
        <button class="send" onclick="ask()">SEND</button>
    </div>

    <div class="buttons">
        <button onclick="speak()">🎙️ SPEAK</button>
        <button onclick="voice()">🔊 VOICE</button>
        <button onclick="searchGoogle()">🔎 GOOGLE</button>
        <button onclick="openYouTube()">▶ YOUTUBE</button>
        <button onclick="openChatGPT()">AI CHAT</button>
        <button onclick="clearChat()">CLEAR</button>
        <button onclick="fullScreen()">⛶ FULL SCREEN</button>
    </div>
</div>

<div class="footer">
    GILATAR AI 15.0 | PURPLE HOLOGRAM SYSTEM
</div>

<script>
let lastReply = "";

function updateClock() {
    document.getElementById("clock").textContent =
        new Date().toLocaleTimeString();
}
setInterval(updateClock, 1000);
updateClock();

function addMessage(text, type) {
    let chat = document.getElementById("chat");
    let div = document.createElement("div");
    div.className = "message " + type;
    div.textContent = text;
    chat.appendChild(div);
    chat.scrollTop = chat.scrollHeight;
}

async function ask() {
    let box = document.getElementById("msg");
    let question = box.value.trim();

    if (!question) return;

    addMessage("YOU: " + question, "user");
    box.value = "";

    let loading = document.createElement("div");
    loading.className = "message bot";
    loading.textContent = "GILATAR: ઇન્ટરનેટ પર શોધી રહ્યો છું... 🌐";
    document.getElementById("chat").appendChild(loading);

    try {
        let response = await fetch("/ask", {
            method: "POST",
            headers: {"Content-Type": "application/json"},
            body: JSON.stringify({question: question})
        });

        if (!response.ok) throw new Error("Server Error");

        let data = await response.json();
        lastReply = data.reply;

        loading.textContent = "GILATAR: " + data.reply;
        document.getElementById("chat").scrollTop =
            document.getElementById("chat").scrollHeight;

    } catch (error) {
        loading.textContent =
            "GILATAR: Connection Error! ફરી પ્રયાસ કરો.";
    }
}

function voice() {
    if (!lastReply) {
        alert("પહેલાં GILATAR ને પ્રશ્ન પૂછો.");
        return;
    }

    if (!("speechSynthesis" in window)) {
        alert("આ બ્રાઉઝરમાં Voice ઉપલબ્ધ નથી.");
        return;
    }

    speechSynthesis.cancel();
    let utterance = new SpeechSynthesisUtterance(lastReply);
    utterance.lang = "gu-IN";
    utterance.rate = 0.9;
    speechSynthesis.speak(utterance);
}

function speak() {
    let Recognition =
        window.SpeechRecognition ||
        window.webkitSpeechRecognition;

    if (!Recognition) {
        alert("તમારા બ્રાઉઝરમાં Speech Recognition ઉપલબ્ધ નથી.");
        return;
    }

    let recognition = new Recognition();
    recognition.lang = "gu-IN";
    recognition.interimResults = false;

    recognition.onresult = function(event) {
        document.getElementById("msg").value =
            event.results[0][0].transcript;
        ask();
    };

    recognition.onerror = function() {
        alert("Microphone અથવા Speech Recognition Error.");
    };

    recognition.start();
}

function searchGoogle() {
    let q = document.getElementById("msg").value.trim();
    if (!q) {
        alert("પહેલાં પ્રશ્ન લખો.");
        return;
    }
    window.open(
        "https://www.google.com/search?q=" +
        encodeURIComponent(q), "_blank"
    );
}

function openYouTube() {
    window.open("https://www.youtube.com", "_blank");
}

function openChatGPT() {
    window.open("https://chatgpt.com", "_blank");
}

function clearChat() {
    document.getElementById("chat").innerHTML = "";
    lastReply = "";
}

function fullScreen() {
    if (!document.fullscreenElement) {
        document.documentElement.requestFullscreen()
        .catch(() => alert("Fullscreen ઉપલબ્ધ નથી."));
    } else {
        document.exitFullscreen();
    }
}
</script>

</body>
</html>
"""


# =========================
# FLASK ROUTES
# =========================

@app.route("/")
def home():
    return render_template_string(HTML)


@app.route("/ask", methods=["POST"])
def ask():
    data = request.get_json(silent=True) or {}
    question = data.get("question", "")
    reply = brain(str(question))
    return jsonify({"reply": reply})


# =========================
# START SERVER
# =========================

if __name__ == "__main__":
    print("=" * 40)
    print("GILATAR AI 15.0 STARTED")
    print("MULTI-PROVIDER INTERNET SEARCH EDITION")
    print("http://127.0.0.1:5000")
    print("=" * 40)

    app.run(host="0.0.0.0", port=5000, debug=False)
