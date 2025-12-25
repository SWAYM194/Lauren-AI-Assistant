# ================= IMPORTS =================
import asyncio
import edge_tts
import os
import datetime
import webbrowser
import subprocess
import urllib.parse
from playsound import playsound
import speech_recognition as sr
from ctypes import cast, POINTER
from comtypes import CLSCTX_ALL
from pycaw.pycaw import AudioUtilities, IAudioEndpointVolume
from groq import Groq
from dotenv import load_dotenv

# ================= ENV =================
load_dotenv()

# ================= CONFIG =================
VOICE = "hi-IN-SwaraNeural"
WAKE_WORD = "lauren"

# ================= AI CLIENT =================
client = Groq(
    api_key=os.getenv("GROQ_API_KEY")
)

# ================= VOICE =================
async def speak(text):
    file = "lauren_voice.mp3"
    await edge_tts.Communicate(text, VOICE).save(file)
    playsound(file)
    try:
        os.remove(file)
    except:
        pass

# ================= LISTEN =================
def listen():
    r = sr.Recognizer()
    r.pause_threshold = 1.8
    r.energy_threshold = 200

    with sr.Microphone() as source:
        print("Listening...")
        r.adjust_for_ambient_noise(source, duration=1)
        audio = r.listen(source, phrase_time_limit=12)

    try:
        text = r.recognize_google(audio)
        print("You said:", text)
        return text.lower()
    except:
        return ""

# ================= AI BRAIN =================
def ai_reply(command):
    research_keywords = [
        "what is", "how to", "explain", "steps", "process",
        "guide", "tutorial", "learn", "meaning"
    ]

    is_research = any(k in command for k in research_keywords)

    if is_research:
        system_prompt = (
            "You are Lauren, an Indian female AI research assistant. "
            "Explain in DETAIL using headings, numbered steps, examples, "
            "and practical tips. Use Hinglish. Be clear and structured."
        )
        max_tokens = 800
    else:
        system_prompt = (
            "You are Lauren, a friendly Indian AI assistant. "
            "Reply shortly and naturally in Hinglish."
        )
        max_tokens = 200

    response = client.chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": command}
        ],
        max_tokens=max_tokens,
        temperature=0.6
    )

    return response.choices[0].message.content

# ================= SYSTEM CONTROLS =================
def volume_up():
    v = AudioUtilities.GetSpeakers().Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )
    cast(v, POINTER(IAudioEndpointVolume)).SetMasterVolumeLevelScalar(0.9, None)

def volume_down():
    v = AudioUtilities.GetSpeakers().Activate(
        IAudioEndpointVolume._iid_, CLSCTX_ALL, None
    )
    cast(v, POINTER(IAudioEndpointVolume)).SetMasterVolumeLevelScalar(0.2, None)

def open_apps(command):
    if "chrome" in command:
        os.startfile("C:\\Program Files\\Google\\Chrome\\Application\\chrome.exe")

    elif "vs code" in command or "visual studio" in command:
        os.startfile("C:\\Users\\DELL\\AppData\\Local\\Programs\\Microsoft VS Code\\Code.exe")

    elif "notepad" in command:
        os.system("notepad")

    elif "discord" in command:
        os.startfile("C:\\Users\\DELL\\AppData\\Local\\Discord\\Update.exe")

    elif "whatsapp" in command:
        webbrowser.open("https://web.whatsapp.com")

# ================= SPOTIFY PLAY =================
def play_spotify_song(command):
    song = command.replace("play", "").replace("song", "").strip()
    if song:
        query = urllib.parse.quote(song)
        url = f"https://open.spotify.com/search/{query}"
        webbrowser.open(url)
        return song
    return None

# ================= START =================
asyncio.run(speak("Namaste Swaym. Main Lauren hoon. Ready hoon."))

while True:
    command = listen()
    if not command:
        continue

    # Wake word
    if command.strip() == WAKE_WORD:
        asyncio.run(speak("Haan Swaym, bolo."))
        continue

    # Time
    if "time" in command:
        now = datetime.datetime.now().strftime("%I:%M %p")
        asyncio.run(speak(f"Abhi time hai {now}"))
        continue

    # Volume
    if "volume up" in command:
        volume_up()
        asyncio.run(speak("Volume badha diya"))
        continue

    if "volume down" in command:
        volume_down()
        asyncio.run(speak("Volume kam kar diya"))
        continue

    # Shutdown
    if "shutdown" in command:
        subprocess.call("shutdown -s -t 60", shell=True)
        asyncio.run(speak("System ek minute me shutdown hoga"))
        continue

    if "cancel shutdown" in command:
        subprocess.call("shutdown -a", shell=True)
        asyncio.run(speak("Shutdown cancel kar diya"))
        continue

    # Spotify
    if command.startswith("play"):
        song = play_spotify_song(command)
        if song:
            asyncio.run(speak(f"Spotify pe {song} chala rahi hoon Swaym"))
            continue

    # Open apps
    if command.startswith("open"):
        open_apps(command)
        asyncio.run(speak("Open kar diya Swaym"))
        continue

    # Exit
    if "exit" in command or "bye" in command:
        asyncio.run(speak("Bye Swaym. Main yahin hoon."))
        break

    # AI Response
    asyncio.run(speak("Thoda rukna Swaym, main soch rahi hoon."))
    reply = ai_reply(command)
    print("Lauren:", reply)
    asyncio.run(speak(reply))
