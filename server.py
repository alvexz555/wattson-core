from flask import Flask, jsonify, request, send_from_directory

from main import WattsonCore

class TemporaryAIProvider:
"""
Provedor temporário de IA.

```
Existe apenas para permitir que o Wattson Core
funcione enquanto o provedor real de IA ainda
está sendo implementado.
"""

def generate(self, message: str) -> str:
    return (
        "O provedor de IA ainda não foi conectado. "
        f"Recebi sua mensagem: {message}"
    )
```

app = Flask(**name**)

ai_provider = TemporaryAIProvider()

wattson = WattsonCore(ai_provider)

@app.get("/")
def index():
return send_from_directory(
".",
"index.html"
)

@app.post("/api/think")
def think():
data = request.get_json(silent=True) or {}

```
message = data.get("message", "")

if not isinstance(message, str):
    return jsonify({
        "error": "A mensagem precisa ser um texto."
    }), 400

message = message.strip()

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
```

if **name** == "**main**":
app.run(
host="0.0.0.0",
port=5000,
debug=True
)
