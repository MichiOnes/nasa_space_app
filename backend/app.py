import os
os.environ.setdefault("MPLBACKEND", "Agg")  # headless plotting

from flask import Flask, request, jsonify, render_template
from flask_cors import CORS
from werkzeug.middleware.proxy_fix import ProxyFix

# Tus utilidades (ajusta el import a donde estén realmente)
from pipeline import build_quiz_objects, parse_questions, txt  # txt = tu bloque de preguntas
from user import get_climate_at_location
from feedback import generate_feedback, provide_feedback_plot
import numpy as np
from IPython.display import display, Image
import base64
import matplotlib.pyplot as plt

app = Flask(__name__, static_folder="static", static_url_path="/static")
CORS(app)
app.wsgi_app = ProxyFix(app.wsgi_app)

#HOST = os.getenv("HOST", "10.236.250.35")
HOST = os.getenv("HOST", "localhost")
PORT = os.getenv("PORT", 5000)

# -------------------------------
# RUTA 1: Página principal (HTML)
# -------------------------------
@app.get("/")
def index():
    return render_template("index.html")

# -------------------------------
# RUTA 2: API to obtain climate by lat/lon
# -------------------------------
@app.post("/api/climate")
def api_climate():
    data = request.get_json(force=True) or {}
    print ("Received data:", data)  # Debugging line
    lat = data.get("lat")
    lon = data.get("lon")

    if lat is None or lon is None:
        
        return jsonify({"error": "Missing lat or lon"}), 400

    climate = get_climate_at_location(lat, lon)
    return jsonify({"lat": lat, "lon": lon, "climate": climate})

# -------------------------------
# RUTA 3: API to generate quiz by lat/lon
# -------------------------------
@app.post("/api/quiz")
def api_quiz():
    data = request.get_json(force=True) or {}
    lat = data.get("lat")
    lon = data.get("lon")
    category = data.get("category")   
    num_options = int(data.get("num_options", 4))

    if lat is None or lon is None:
        return jsonify({"error": "Missing lat or lon"}), 400

    # 1) Determine climate at location
    user_climate = get_climate_at_location(lat, lon)

    # 2) Parse questions from your source text 
    categories_dict = parse_questions(txt)

    # 3) Construir quiz adaptado al clima
    quiz_for_app = build_quiz_objects(categories_dict, user_climate, num_options=num_options)

    return jsonify({
        "lat": lat,
        "lon": lon,
        "climate": user_climate,
        "quiz": quiz_for_app
    })

# -------------------------------
# RUTA 4: API to generate results/feedback
# -------------------------------

PATH = './data/final_data.npz'
data = np.load(PATH)

@app.post("/api/feedback")
def api_feedback():
    payload = request.get_json(force=True) or {}

    # Ajusta los nombres según lo que envíe tu frontend
    user_input = payload.get("user_input")     # p.ej. respuestas del usuario

    if user_input is None:
        return jsonify({"error": "Missing user_input"})

    feedback_json = generate_feedback(user_input, data)

    # NO uses display() en un endpoint; eso no llega al navegador.
    # Devuelve el JSON (incluido el base64 del plot si lo generas):

    print ("Feedback JSON:", feedback_json)  # Para depuración en consola
    return jsonify(feedback_json)

# ---- Health ----
@app.get("/health")
def health():
    return {"ok": True}

if __name__ == "__main__":
    app.run(host=HOST, port=PORT, debug=True)
