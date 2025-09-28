# app.py
from flask import Flask, request, jsonify
from shr_parser import parse_shr  # импортируем твой скрипт
from flask_cors import CORS

app = Flask(__name__)
CORS(app)
@app.route("/parse", methods=["POST"])
def parse_shr_api():
    data = request.json
    shr_text = data.get("shr")
    if not shr_text:
        return jsonify({"error": "No SHR string provided"}), 400
    try:
        result = parse_shr(shr_text)
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(debug=True)
