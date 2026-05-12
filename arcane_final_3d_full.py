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
VOICE_ID = os.getenv("VOICE_ID") or "buUrS4YSeOZtlCKnzwkC"
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")

# ---------- Alte Funktionen ----------
def load_json(f):
    p = os.path.join(DESKTOP, f)
    if os.path.exists(p):
        with open(p,"r",encoding="utf-8") as fp:
            return json.load(fp)
    return []

def save_json(f,data):
    p = os.path.join(DESKTOP,f)
    with open(p,"w",encoding="utf-8") as fp:
        json.dump(data,fp,ensure_ascii=False,indent=2)

def get_wetter():
    try:
        r = requests.get(f"http://api.openweathermap.org/data/2.5/weather?q=Bremen,DE&appid={WEATHER_KEY}&units=metric&lang=de")
        d = r.json()
        return f"{round(d['main']['temp'])}C, {d['weather'][0]['description']}"
    except:
        return "Wetterdaten nicht verfügbar"

# ---------- Chat ----------
@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get("messages",[])
    # Simulierter Chat-Reply
    return jsonify({"reply":"Hallo Sir, dies ist ein Test-Chat-Reply.","commands":[]})

# ---------- Speak ----------
@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    return Response(b"", mimetype="audio/mpeg")

# ---------- Transcribe ----------
@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio = request.files['file']
    return jsonify({"text": "Simuliertes Transcribe-Ergebnis"})

# ---------- Notes / Reminders / Archive ----------
@app.route('/data/notes', methods=['GET'])
def get_notes(): return jsonify(load_json('notizen.json'))

@app.route('/data/reminders', methods=['GET'])
def get_reminders(): return jsonify(load_json('erinnerungen.json'))

@app.route('/data/archive', methods=['GET'])
def get_archive(): return jsonify(load_json('archiv.json'))

# ---------- Greet ----------
@app.route('/greet', methods=['GET'])
def greet():
    n = datetime.now()
    return jsonify({"text": f"Guten Tag, Sir. Es ist {n.strftime('%A, %d.%m.%Y %H:%M Uhr')}"})

# ---------- Scan ----------
@app.route('/scan', methods=['POST'])
def scan_object():
    image = request.files['file']
    result = {
        "name": "Beliebiges Objekt",
        "material": "Unbekannt",
        "details": "Simulierte Objektdaten"
    }
    return jsonify(result)

# ---------- 3D Generation (asynchron) ----------
@app.route('/generate_3d', methods=['POST'])
def generate_3d():
    object_name = request.json.get("object","Unbekannt")
    
    # Blender im Hintergrund starten
    subprocess.Popen([
        "blender",
        "--background",
        "--python",
        "blender_generate_model.py",
        "--",
        object_name
    ])
    
    return jsonify({"status":"3D-Auftrag gestartet","object":object_name})

# ---------- Alte PC-Befehle & Programme ----------
@app.route('/pc_command', methods=['POST'])
def pc_command():
    data = request.json
    cmd = data.get("command","")
    # Dummy, simuliert alte PC-Steuerung
    return jsonify({"status":f"Command '{cmd}' empfangen"})

# ---------- Notizen & Erinnerungen speichern ----------
@app.route('/save_note', methods=['POST'])
def save_note():
    note = request.json.get("text","")
    notes = load_json("notizen.json")
    notes.append({"text":note,"datum":datetime.now().strftime("%d.%m.%Y %H:%M")})
    save_json("notizen.json", notes)
    return jsonify({"status":"Notiz gespeichert"})

@app.route('/save_reminder', methods=['POST'])
def save_reminder():
    rem = request.json
    reminders = load_json("erinnerungen.json")
    reminders.append(rem)
    save_json("erinnerungen.json", reminders)
    return jsonify({"status":"Erinnerung gespeichert"})

# ---------- Server starten ----------
if __name__ == '__main__':
    print("A.R.C.A.N.E. 3D Server läuft lokal")
    port = int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0", port=port, debug=False)
