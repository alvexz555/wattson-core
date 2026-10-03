from wattson_core.ai.context import ConversationContext
from wattson_core.ai.engine import AIEngine
from wattson_core.ai.session import Session
from wattson_core.ai.conversation import ConversationAI
from wattson_core.core.orchestrator import Orchestrator


class FakeProvider:
    def generate(self, prompt: str) -> str:
        messages = prompt.split("\n")

        if "qual é seu nome" in prompt.lower():
            return "Meu nome é Wattson."

        if "meu nome é arise" in prompt.lower():
            return "Prazer, A.RISE. Vou manter isso no contexto desta sessão."

        if "qual foi a mensagem anterior" in prompt.lower():
            return f"A mensagem anterior foi: {messages[-2]}"

        return f"Recebi sua mensagem: {messages[-1]}"


session = Session()
context = session.context

engine = AIEngine(FakeProvider())
conversation = ConversationAI(engine, context)
orchestrator = Orchestrator(conversation)


print("=" * 50)
print("WATTSON CORE - TESTE PRÁTICO")
print("=" * 50)
print("Digite 'sair' para encerrar.")
print()

while session.active:
    message = input("Você: ")

    if message.lower() == "sair":
        session.close()
        break

    response = orchestrator.handle(message)
    print(f"Wattson: {response}")
