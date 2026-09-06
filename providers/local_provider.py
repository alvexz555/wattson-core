import requests


class LocalAIProvider:
    """
    Provedor de IA local usando Ollama.
    """

    def __init__(
        self,
        model="gemma4:e2b",
        base_url="http://127.0.0.1:11434"
    ):
        self.model = model
        self.base_url = base_url

    def generate(self, message: str) -> str:
        """
        Envia uma mensagem para o Ollama
        e retorna a resposta do modelo.
        """

        response = requests.post(
            f"{self.base_url}/api/generate",
            json={
                "model": self.model,
                "prompt": message,
                "stream": False
            },
            timeout=120
        )

        response.raise_for_status()

        data = response.json()

        return data["response"]
