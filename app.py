
from flask import Flask, request, jsonify, render_template_string
from datetime import datetime
import random

app = Flask(__name__)

# =========================
# GILATAR AI 11.0 BRAIN
# =========================

def brain(q):
    q = q.lower().strip()

    if not q:
        return "કૃપા કરીને કંઈક લખો. 😊"

    if any(x in q for x in ["hello", "hi", "નમસ્તે", "હેલો"]):
        return "નમસ્તે! 💜 હું GILATAR AI 11.0 છું. તમારી મદદ માટે તૈયાર છું!"

    if "તમારું નામ" in q or "your name" in q:
        return "મારું નામ GILATAR AI 11.0 છે. 💜"

    if "કેમ છો" in q or "how are you" in q:
        return "હું એકદમ સરસ છું! તમે કેમ છો? 😊"

    if "સમય" in q or "time" in q:
        return "હાલનો સમય: " + datetime.now().strftime("%I:%M %p")

    if "તારીખ" in q or "date" in q:
        return "આજની તારીખ: " + datetime.now().strftime("%d-%m-%Y")

    if "ગુજરાતની રાજધાની" in q:
        return "ગુજરાતની રાજધાની ગાંધીનગર છે."

    if "ભારતની રાજધાની" in q:
        return "ભારતની રાજધાની નવી દિલ્હી છે."

    if "ભારતના વડાપ્રધાન" in q:
        return "ભારતના વડાપ્રધાન વિશેની નવીનતમ માહિતી માટે Google Search કરો."

    if "જોક" in q or "joke" in q:
        return random.choice([
            "શિક્ષક: હોમવર્ક ક્યાં છે? વિદ્યાર્થી: સર, ઘરે જ છે! 😂",
            "કમ્પ્યુટર કેમ ઠંડું રહે છે? કારણ કે તેની પાસે Windows છે! 😄",
            "મોબાઇલ બોલ્યો: મને ચાર્જ કરો, હું પણ થાકી ગયો છું! 😂"
        ])

    if "આભાર" in q or "thank" in q:
        return "તમારું સ્વાગત છે! 💜"

    if "બાય" in q or "bye" in q:
        return "આવજો! ફરી મળીએ. 💜"

    if "મદદ" in q or "help" in q:
        return (
            "હું આ પ્રશ્નોના જવાબ આપી શકું છું:\n"
            "• સમય અને તારીખ\n"
            "• ગુજરાત અને ભારતની રાજધાની\n"
            "• જોક્સ\n"
            "• મારું નામ\n"
            "વધુ માહિતી માટે Google Search વાપરો."
        )

    return (
        "આ પ્રશ્નનો જવાબ મારી Offline Knowledge માં નથી. 💜\n"
        "વધુ માહિતી માટે GOOGLE SEARCH બટન દબાવો."
    )


# =========================
# FUTURISTIC HOLOGRAM UI
# =========================

HTML = r"""
<!DOCTYPE html>
<html lang="gu">
<head>
<meta charset="UTF-8">
<meta name="viewport"
content="width=device-width, initial-scale=1.0">

<title>GILATAR AI 11.0</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    min-height: 100vh;
    background:
        radial-gradient(ellipse at 50% 35%,
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
    mask-image: linear-gradient(transparent, black, transparent);
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
    text-shadow:
        0 0 8px #c56aff,
        0 0 22px #a020f0;
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
    box-shadow: 0 0 15px #a832ff,
                inset 0 0 15px #a832ff;
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
        #f4d9ff 0%,
        #c65aff 20%,
        #7217c7 55%,
        #180526 100%);
    box-shadow: 0 0 20px #bc52ff,
                0 0 55px #9c27ff,
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
    0%, 100% {
        transform: scale(1);
        filter: brightness(1);
    }
    50% {
        transform: scale(1.08);
        filter: brightness(1.4);
    }
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
    height: 260px;
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

input:focus {
    box-shadow: 0 0 12px #a832ff;
}

button {
    padding: 12px 15px;
    border: 1px solid #c36aff;
    border-radius: 10px;
    background: linear-gradient(135deg,
        #60208b, #260b40);
    color: white;
    font-weight: bold;
    cursor: pointer;
    transition: .2s;
}

button:active {
    transform: scale(.95);
    background: #a832ff;
}

.send {
    background: linear-gradient(135deg,
        #a832ff, #6013a0);
}

.buttons {
    display: flex;
    flex-wrap: wrap;
    justify-content: center;
    gap: 8px;
    margin-top: 13px;
}

.buttons button {
    flex: 1 1 120px;
}

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
    .ring.three {
        width: 215px;
        height: 215px;
    }
    .chat { height: 280px; }
    button { padding: 12px 10px; }
}
</style>
</head>

<body>

<header>
    <div class="logo">GILATAR AI</div>
    <div class="version">11.0 FUTURISTIC HOLOGRAM</div>
    <div class="status">● SYSTEM ONLINE</div>
</header>

<div class="reactor-area">
    <div class="ring three"></div>
    <div class="ring"></div>
    <div class="ring two"></div>
    <div class="core">GILATAR<br>AI 11.0</div>
</div>

<div class="clock" id="clock">00:00:00</div>

<div class="panel">

    <div class="chat" id="chat">
        <div class="message bot">
            GILATAR: નમસ્તે! 💜
            હું GILATAR AI 11.0 છું.
            તમારી મદદ માટે તૈયાર છું!
        </div>
    </div>

    <div class="input-area">
        <input id="msg"
        placeholder="તમારો પ્રશ્ન લખો..."
        onkeydown="if(event.key==='Enter') ask()">

        <button class="send" onclick="ask()">
            SEND
        </button>
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
    GILATAR AI 11.0 | PURPLE HOLOGRAM SYSTEM
</div>

<script>

let lastReply = "";

function updateClock() {
    let now = new Date();

    document.getElementById("clock").textContent =
        now.toLocaleTimeString();
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

    try {
        let response = await fetch("/ask", {
            method: "POST",
            headers: {
                "Content-Type": "application/json"
            },
            body: JSON.stringify({
                question: question
            })
        });

        if (!response.ok) {
            throw new Error("Server Error");
        }

        let data = await response.json();

        lastReply = data.reply;
        addMessage("GILATAR: " + data.reply, "bot");

    } catch (error) {
        addMessage(
            "Connection Error! Server ચાલુ છે કે નહીં તપાસો.",
            "bot"
        );
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

    let utterance =
        new SpeechSynthesisUtterance(lastReply);

    utterance.lang = "gu-IN";
    utterance.rate = 0.9;
    utterance.pitch = 1;

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
        alert("પહેલાં Search માટે પ્રશ્ન લખો.");
        return;
    }

    window.open(
        "https://www.google.com/search?q=" +
        encodeURIComponent(q),
        "_blank"
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
        .catch(() => {
            alert("Fullscreen ઉપલબ્ધ નથી.");
        });
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

    return jsonify({
        "reply": reply
    })


# =========================
# START SERVER
# =========================

if __name__ == "__main__":
    print("=" * 40)
    print("GILATAR AI 11.0 STARTED")
    print("PURPLE FUTURISTIC HOLOGRAM")
    print("http://127.0.0.1:5000")
    print("=" * 40)

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False
    )
