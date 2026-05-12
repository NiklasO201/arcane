from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import json
import os
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Environment-Keys für Railway
CLAUDE_KEY = os.getenv("CLAUDE_KEY")
ELEVEN_KEY = os.getenv("ELEVEN_KEY")
WEATHER_KEY = os.getenv("WEATHER_KEY")
TAVILY_KEY = os.getenv("TAVILY_KEY")
VOICE_ID = os.getenv("VOICE_ID") or "buUrS4YSeOZtlCKnzwkC"
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")

def load_json(f):
    p = os.path.join(DESKTOP, f)
    if os.path.exists(p):
        with open(p, "r", encoding="utf-8") as fp:
            return json.load(fp)
    return []

def save_json(f, data):
    p = os.path.join(DESKTOP, f)
    with open(p, "w", encoding="utf-8") as fp:
        json.dump(data, fp, ensure_ascii=False, indent=2)

def get_wetter():
    try:
        r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Bremen,DE&appid={WEATHER_KEY}&units=metric&lang=de")
        d = r.json()
        return f"{round(d['main']['temp'])}C, {d['weather'][0]['description']}"
    except:
        return "Wetterdaten nicht verfuegbar"

def web_suche(query):
    try:
        r = requests.post("https://api.tavily.com/search", json={
            "api_key": TAVILY_KEY, "query": query,
            "search_depth": "basic", "max_results": 3
        })
        d = r.json()
        result = ""
        for res in d.get("results", []):
            result += f"- {res['title']}: {res['content'][:200]}\n"
        return result or "Keine Ergebnisse."
    except:
        return "Websuche nicht verfuegbar."

def build_system():
    tage = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
    jetzt = datetime.now()
    wochentag = tage[jetzt.weekday()]
    datum = jetzt.strftime("%d.%m.%Y")
    uhrzeit = jetzt.strftime("%H:%M Uhr")
    wetter = get_wetter()
    erinnerungen = load_json("erinnerungen.json")
    notizen = load_json("notizen.json")
    archiv = load_json("archiv.json")

    return f"""Du bist A.R.C.A.N.E. - Artificial Reasoning & Cognitive Assistant for Natural Execution.
Direkt, kuehl, professionell. Kein Markdown, keine Emojis, keine Sternchen. Nur klarer Fliesstext. Kurze praezise Antworten. Sprich den Nutzer immer mit Sir an.
Nutzer: Niklas, 24, Bremen, Industriemechaniker, baut Selbstaendigkeit auf, hat ADHS, Figurenmarke MORVEX, TikTok morvex.officiall. Ziel: Selbstaendigkeit.

Aktuelle Zeit: {wochentag}, {datum}, {uhrzeit}
Aktuelles Wetter Bremen: {wetter}
Aktive Erinnerungen: {erinnerungen}
Gespeicherte Notizen: {notizen}
Archiv: {archiv}

BEFEHLE - nur in separaten Zeilen ohne zusaetzliche Worte:
Websuche: WEBSUCHE|Suchbegriff
Erinnerung heute: ERINNERUNG|HH:MM|Text
Erinnerung mit Datum: ERINNERUNG|HH:MM|DD.MM.YYYY|Text
Notiz speichern: NOTIZ|Text
Panel wechseln (nur wenn sinnvoll): SWITCH|notes oder SWITCH|rem oder SWITCH|arch oder SWITCH|chat
PC herunterfahren: PC_SHUTDOWN
PC Neustart: PC_NEUSTART
Ruhemodus: PC_RUHEMODUS
ARCANE Neustart: ARCANE_NEUSTART
Programm oeffnen: PROGRAMM|Programmname

Bei Fragen nach aktuellen Nachrichten oder Ereignissen: SOFORT WEBSUCHE ohne zu fragen.
Beim ersten Start begruessung mit Uhrzeit und Wetter."""

@app.route('/greet', methods=['GET'])
def greet():
    tage = ["Montag","Dienstag","Mittwoch","Donnerstag","Freitag","Samstag","Sonntag"]
    n = datetime.now()
    wochentag = tage[n.weekday()]
    datum = n.strftime("%d.%m.%Y")
    uhrzeit = n.strftime("%H:%M Uhr")
    wetter = get_wetter()
    stunde = n.hour
    if stunde < 12: gruss = "Guten Morgen"
    elif stunde < 18: gruss = "Guten Tag"
    else: gruss = "Guten Abend"
    erinnerungen = load_json("erinnerungen.json")
    heute = n.strftime("%d.%m.%Y")
    heutige = [e for e in erinnerungen if e.get("datum","") == heute or e.get("datum","") == ""]
    text = f"{gruss}, Sir. Es ist {wochentag}, {datum}, {uhrzeit}. Aktuelles Wetter in Bremen: {wetter}."
    if heutige:
        text += " Heutige Erinnerungen: " + ", ".join([f"{e['zeit']} Uhr: {e['text']}" for e in heutige]) + "."
    return jsonify({"text": text})

# (Hier alle deine Chat, Speak, Transcribe, Notes, Reminders Routen einfügen, wie in deinem Originalcode)

if __name__ == '__main__':
    print("A.R.C.A.N.E. Server läuft auf Railway")
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port, debug=False)
