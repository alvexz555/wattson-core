```python
class WattsonCore:
    """
    Primeira versão experimental do Wattson Core.

    Esta IA:
    - recebe uma mensagem;
    - identifica uma intenção simples;
    - toma uma decisão;
    - responde.
    """

    def __init__(self):
        self.name = "Wattson"
        self.version = "0.1.0"

    def think(self, message: str) -> str:
        """
        Analisa a mensagem e escolhe uma resposta.
        """

        text = message.lower().strip()

        if not text:
            return "Não recebi nenhuma entrada."

        if "olá" in text or "oi" in text:
            return "Olá. Eu sou o Wattson Core."

        if "quem é você" in text or "quem você é" in text:
            return "Sou o Wattson Core, uma inteligência artificial experimental."

        if "como você está" in text:
            return "Todos os meus sistemas estão funcionando."

        if "tchau" in text or "adeus" in text:
            return "Até a próxima."

        if "teste" in text:
            return "Teste recebido. Meu sistema de decisão está funcionando."

        return "Ainda não sei como responder a isso."


def main():
    wattson = WattsonCore()

    print("=" * 40)
    print(f"{wattson.name} Core v{wattson.version}")
    print("Sistema iniciado.")
    print("=" * 40)

    tests = [
        "Olá Wattson",
        "Quem é você?",
        "Como você está?",
        "Isso é um teste",
        "Tchau"
    ]

    for message in tests:
        print(f"\nVocê: {message}")

        response = wattson.think(message)

        print(f"Wattson: {response}")


if __name__ == "__main__":
    main()
```
