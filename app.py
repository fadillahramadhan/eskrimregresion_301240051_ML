"""
app.py - Aplikasi web Flask: Prediksi Pendapatan Toko Es Krim berdasarkan Suhu
Jalankan lokal : python app.py
Produksi       : gunicorn app:app
"""
import json
import os

import joblib
import pandas as pd
from flask import Flask, jsonify, render_template, request

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_PATH = os.path.join(BASE_DIR, "model", "model_regresi_linear.joblib")
METRICS_PATH = os.path.join(BASE_DIR, "model", "metrics.json")

app = Flask(__name__)
model = joblib.load(MODEL_PATH)
with open(METRICS_PATH, encoding="utf-8") as f:
    METRICS = json.load(f)

T_MIN, T_MAX = METRICS["temp_min"], METRICS["temp_max"]


def prediksi(suhu: float) -> float:
    return float(model.predict(pd.DataFrame({"Temperature": [suhu]}))[0])


@app.route("/", methods=["GET", "POST"])
def index():
    hasil, suhu, error, catatan = None, None, None, None
    if request.method == "POST":
        raw = request.form.get("suhu", "").strip().replace(",", ".")
        try:
            suhu = float(raw)
            if suhu < -30 or suhu > 60:
                error = "Suhu harus berada di antara -30 dan 60 °C."
            else:
                hasil = max(prediksi(suhu), 0.0)
                if suhu < T_MIN or suhu > T_MAX:
                    catatan = (
                        f"Suhu di luar rentang data latih ({T_MIN:.1f}–{T_MAX:.1f} °C); "
                        "prediksi merupakan ekstrapolasi dan kurang andal."
                    )
        except ValueError:
            error = "Masukkan suhu berupa angka, contoh: 28.5"
    return render_template(
        "index.html", hasil=hasil, suhu=suhu, error=error, catatan=catatan, m=METRICS
    )


@app.route("/api/predict")
def api_predict():
    try:
        suhu = float(request.args.get("suhu", ""))
    except ValueError:
        return jsonify(error="parameter 'suhu' harus angka"), 400
    return jsonify(suhu=suhu, revenue_usd=round(max(prediksi(suhu), 0.0), 2))


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)), debug=False)
