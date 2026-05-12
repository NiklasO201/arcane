from flask import Flask, request, Response, jsonify
from flask_cors import CORS
import requests
import json
import os
import subprocess
from datetime import datetime

app = Flask(__name__)
CORS(app)

# ---------------------------
# Environment Keys für Railway
# ---------------------------
CLAUDE_KEY = os.getenv("CLAUDE_KEY")
ELEVEN_KEY = os.getenv("ELEVEN_KEY")
WEATHER_KEY = os.getenv("WEATHER_KEY")
TAVILY_KEY = os.getenv("TAVILY_KEY")
VOICE_ID = os.getenv("VOICE_ID") or "buUrS4YSeOZtlCKnzwkC"
DESKTOP = os.path.join(os.path.expanduser("~"), "Desktop")

# ---------------------------
# Bestehende Funktionen (Chat, Greet, Speak, Transcribe, Notes, Reminders)
# ---------------------------

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
        return "Wetterdaten nicht verfuegbar"

@app.route('/chat', methods=['POST'])
def chat():
    data = request.json
    messages = data.get("messages",[])
    return jsonify({"reply":"Simulierter Chat-Reply","commands":[]})

@app.route('/speak', methods=['POST'])
def speak():
    data = request.json
    return Response(b"", mimetype="audio/mpeg")

@app.route('/transcribe', methods=['POST'])
def transcribe():
    audio = request.files['file']
    return jsonify({"text": "Simuliertes Transcribe-Ergebnis"})

@app.route('/data/notes', methods=['GET'])
def get_notes(): return jsonify(load_json('notizen.json'))

@app.route('/data/reminders', methods=['GET'])
def get_reminders(): return jsonify(load_json('erinnerungen.json'))

@app.route('/data/archive', methods=['GET'])
def get_archive(): return jsonify(load_json('archiv.json'))

@app.route('/greet', methods=['GET'])
def greet():
    n = datetime.now()
    return jsonify({"text": f"Guten Tag, Sir. Es ist {n.strftime('%d.%m.%Y %H:%M')}."})

# ---------------------------
# Neue Endpoints für 3D + Scan
# ---------------------------

@app.route('/scan', methods=['POST'])
def scan_object():
    image = request.files['file']
    result = {
        "name": "Beliebiges Objekt",
        "material": "Unbekannt",
        "details": "Simulierte Objektdaten"
    }
    return jsonify(result)

@app.route('/generate_3d', methods=['POST'])
def generate_3d():
    object_name = request.json.get("object","Unbekannt")
    # Blender oder externe AI kann hier später eingebunden werden
    model_data = {
        "object": object_name,
        "parts":[
            {"name":"Teil1","vertices":[]},
            {"name":"Teil2","vertices":[]},
            {"name":"Teil3","vertices":[]}
        ]
    }
    return jsonify(model_data)

if __name__ == '__main__':
    print("A.R.C.A.N.E. 3D Server läuft auf Railway")
    port = int(os.environ.get("PORT",8080))
    app.run(host="0.0.0.0", port=port, debug=False)
