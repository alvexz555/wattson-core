from flask import Flask, jsonify, request, send_from_directory
from openai import OpenAI

from main import WattsonCore


app = Flask(__name__, static_folder="interface")

client = OpenAI()

wattson = WattsonCore(client)


@app.get("/")
def index():
    return send_from_directory(
        "interface",
        "index.html"
    )


@app.post("/api/think")
def think():
    data = request.get_json(silent=True) or {}

    message = data.get("message", "").strip()

    if not message:
        return jsonify({
            "error": "Mensagem vazia."
        }), 400

    try:
        response = wattson.think(message)

        return jsonify({
            "response": response
        })

    except Exception as error:
        return jsonify({
            "error": str(error)
        }), 500


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=5000,
        debug=True
    )
