from wattson_core.ai.engine import AIEngine
from wattson_core.ai.conversation import ConversationAI


class FakeProvider:
    def generate(self, prompt: str) -> str:
        return f"Wattson recebeu: {prompt}"


def main():
    provider = FakeProvider()
    engine = AIEngine(provider)
    conversation = ConversationAI(engine)

    print("=" * 50)
    print("        WATTSON - TESTE DE CONVERSA")
    print("=" * 50)
    print("Digite 'sair' para encerrar.")
    print()

    while True:
        message = input("Você: ")

        if message.lower() == "sair":
            print("Wattson: Encerrando sessão.")
            break

        response = conversation.respond(message)

        print(f"Wattson: {response}")
        print()


if __name__ == "__main__":
    main()
