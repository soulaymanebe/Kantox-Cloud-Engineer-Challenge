from flask import Flask, jsonify
from prometheus_flask_exporter import PrometheusMetrics
import requests
import os

VERSION = os.environ.get("MAIN_VERSION", "0.0.1")
AUX_URL = os.environ.get("AUX_URL", "http://aux-service.aux-service.svc.clusterequest.local:5000")

app = Flask(__name__)

metrics = PrometheusMetrics(app)

@app.route("/buckets")
def buckets():
    try:
        request = requests.get(f"{AUX_URL}/buckets")
        data = request.json()
        return jsonify({
            "main_version": VERSION,
            "aux_version": data.get("version"),
            "buckets": data.get("buckets", [])
        })
    except:
        return jsonify({"error": "Cannot reach aux-service"}), 502

@app.route("/params")
def params():
    try:
        request = requests.get(f"{AUX_URL}/params")
        data = request.json()
        return jsonify({
            "main_version": VERSION,
            "aux_version": data.get("version"),
            "parameters": data.get("parameters", [])
        })
    except:
        return jsonify({"error": "Cannot reach aux-service"}), 502

@app.route("/param/<path:name>")
def param(name):
    try:
        request = requests.get(f"{AUX_URL}/param/{name}")
        data = request.json()
        return jsonify({
            "main_version": VERSION,
            "aux_version": data.get("version"),
            "value": data.get("value")
        })
    except:
        return jsonify({"error": "Cannot reach aux-service"}), 502

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=6000)
