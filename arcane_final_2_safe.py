from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import json
import os
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app)

CLAUDE_KEY = os.getenv("CLAUDE_KEY")
ELEVEN_KEY = os.getenv("ELEVEN_KEY")
WEATHER_KEY = os.getenv("WEATHER_KEY")
TAVILY_KEY = os.getenv("TAVILY_KEY")
VOICE_ID = "buUrS4YSeOZtlCKnzwkC"
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

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get("messages", [])
    system = build_system()

    res = requests.post(
        'https://api.anthropic.com/v1/messages',
        headers={'Content-Type':'application/json','x-api-key':CLAUDE_KEY,'anthropic-version':'2023-06-01'},
        json={"model":"claude-sonnet-4-5","max_tokens":1000,"system":system,"messages":messages}
    )
    reply_data = res.json()
    reply = reply_data["content"][0]["text"]

    # Process commands
    lines = reply.split("\n")
    clean_lines = []
    commands = []
    for line in lines:
        stripped = line.strip()
        if stripped.startswith("WEBSUCHE|"):
            query = stripped.split("|",1)[1]
            result = web_suche(query)
            commands.append({"type":"websuche","query":query,"result":result})
        elif stripped.startswith("ERINNERUNG|"):
            parts = stripped.split("|")
            e = {"zeit":parts[1].strip(),"text":parts[-1].strip()}
            if len(parts)==4: e["datum"]=parts[2].strip()
            erinnerungen = load_json("erinnerungen.json")
            erinnerungen.append(e)
            save_json("erinnerungen.json", erinnerungen)
            commands.append({"type":"erinnerung","data":e})
        elif stripped.startswith("NOTIZ|"):
            notiztext = stripped.split("|",1)[1]
            notizen = load_json("notizen.json")
            notizen.append({"text":notiztext,"datum":datetime.now().strftime("%d.%m.%Y %H:%M")})
            save_json("notizen.json", notizen)
            commands.append({"type":"notiz","text":notiztext})
        elif stripped.startswith("SWITCH|"):
            commands.append({"type":"switch","panel":stripped.split("|")[1]})
        elif stripped == "PC_SHUTDOWN":
            commands.append({"type":"pc","action":"shutdown"})
            subprocess.Popen(["shutdown","/s","/t","10"])
        elif stripped == "PC_NEUSTART":
            commands.append({"type":"pc","action":"restart"})
            subprocess.Popen(["shutdown","/r","/t","10"])
        elif stripped == "PC_RUHEMODUS":
            commands.append({"type":"pc","action":"sleep"})
            subprocess.Popen(["rundll32.exe","powrprof.dll,SetSuspendState","0,1,0"])
        elif stripped == "ARCANE_NEUSTART":
            commands.append({"type":"arcane","action":"restart"})
        elif stripped.startswith("PROGRAMM|"):
            prog = stripped.split("|",1)[1]
            subprocess.Popen(prog, shell=True)
            commands.append({"type":"programm","name":prog})
        else:
            clean_lines.append(line)

    clean_reply = "\n".join(clean_lines).strip()

    # If websuche was done, get AI to summarize
    for cmd in commands:
        if cmd["type"] == "websuche":
            res2 = requests.post(
                'https://api.anthropic.com/v1/messages',
                headers={'Content-Type':'application/json','x-api-key':CLAUDE_KEY,'anthropic-version':'2023-06-01'},
                json={"model":"claude-sonnet-4-5","max_tokens":500,"system":build_system(),
                      "messages":messages+[{"role":"user","content":f"Suchergebnisse fuer '{cmd['query']}':\n{cmd['result']}\nFasse das fuer Sir zusammen. Kein Markdown."}]}
            )
            clean_reply = res2.json()["content"][0]["text"]
            break

    # Build final reply text
    if not clean_reply:
        for cmd in commands:
            if cmd["type"]=="erinnerung":
                clean_reply = f"Verstanden, Sir. Erinnerung gesetzt: {cmd['data']['zeit']} Uhr - {cmd['data']['text']}"
            elif cmd["type"]=="notiz":
                clean_reply = f"Notiz gespeichert, Sir: {cmd['text']}"
            elif cmd["type"]=="pc":
                clean_reply = f"Verstanden, Sir. PC wird {cmd['action']}..."
            elif cmd["type"]=="programm":
                clean_reply = f"Programm wird geoeffnet, Sir: {cmd['name']}"

    return jsonify({"reply": clean_reply, "commands": commands})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    vid = data.get('voice_id', VOICE_ID)
    res = requests.post(
        f'https://api.elevenlabs.io/v1/text-to-speech/{vid}',
        headers={'xi-api-key':ELEVEN_KEY,'Content-Type':'application/json'},
        json=data.get('payload')
    )
    return Response(res.content, mimetype='audio/mpeg')

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio = request.files['file']
    res = requests.post(
        'https://api.elevenlabs.io/v1/speech-to-text',
        headers={'xi-api-key':ELEVEN_KEY},
        files={'file':(audio.filename,audio.read(),audio.mimetype)},
        data={'model':'scribe_v1','language':'de'}
    )
    return jsonify(res.json())

@app.route('/data/notes', methods=['GET'])
def get_notes(): return jsonify(load_json('notizen.json'))

@app.route('/data/reminders', methods=['GET'])
def get_reminders(): return jsonify(load_json('erinnerungen.json'))

@app.route('/data/archive', methods=['GET'])
def get_archive(): return jsonify(load_json('archiv.json'))

if __name__ == '__main__':
    print("A.R.C.A.N.E. Server laeuft auf http://localhost:5000")
    port = int(os.environ.get("PORT", 8080))
app.run(host="0.0.0.0", port=port, debug=False)
