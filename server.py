from flask import Flask, jsonify, request, send_from_directory

from main import WattsonCore
from providers.local_provider import LocalAIProvider


app = Flask(__name__)

ai_provider = LocalAIProvider()
wattson = WattsonCore(ai_provider)


@app.route("/", methods=["GET"])
def index():
    return send_from_directory(".", "index.html")


@app.route("/api/think", methods=["POST"])
def think():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str):
        return jsonify({"error": "A mensagem precisa ser um texto."}), 400

    message = message.strip()

    if not message:
        return jsonify({"error": "Mensagem vazia."}), 400

    try:
        response = wattson.think(message)
        return jsonify({"response": response})
    except Exception as error:
        return jsonify({"error": str(error)}), 500


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)
