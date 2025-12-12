from flask import Flask, jsonify, Response
from prometheus_client import generate_latest, CONTENT_TYPE_LATEST
import boto3
import os

VERSION = os.environ.get("AUX_VERSION")
REGION = os.environ.get("AWS_REGION")

app = Flask(__name__)
s3 = boto3.client('s3')
ssm = boto3.client('ssm', region_name=REGION)

@app.route("/metrics")
def expose_metrics():
    return Response(generate_latest(), mimetype=CONTENT_TYPE_LATEST)

@app.route("/healthz")
def healthz():
    return "OK", 200

@app.route("/buckets")
def list_buckets():
    try:
        response = s3.list_buckets()
        buckets = [b['Name'] for b in response.get('Buckets', [])]
        return jsonify({
            "version": VERSION,
            "buckets": buckets
        })
    except:
        return jsonify({"error": "Cannot list buckets"}), 500

@app.route("/params")
def list_params():
    try:
        response = ssm.describe_parameters()
        params = [p['Name'] for p in response.get('Parameters', [])]
        return jsonify({
            "version": VERSION,
            "parameters": params
        })
    except:
        return jsonify({"error": "Cannot list parameters"}), 500

@app.route("/param/<path:name>")
def get_param(name):
    if not name.startswith("/"):
        name = "/" + name
    try:
        param = ssm.get_parameter(Name=name, WithDecryption=True)
        return jsonify({
            "version": VERSION,
            "value": param['Parameter']['Value']
        })
    except:
        return jsonify({"error": "Parameter not found or cannot fetch"}), 404

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)
