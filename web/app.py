"""HTTP health endpoints."""
from flask import Flask,jsonify
app=Flask(__name__)
@app.get("/")
def index():return jsonify({"ok":True,"service":"telegram-bot"})
@app.get("/health")
def health():return jsonify({"ok":True,"status":"healthy"}),200
