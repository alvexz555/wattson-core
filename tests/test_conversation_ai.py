from wattson_core.ai.conversation import ConversationAI
from wattson_core.ai.engine import AIEngine
from wattson_core.ai.context import ConversationContext


class FakeProvider:
    def generate(self, prompt: str) -> str:
        return f"resposta: {prompt}"


def test_conversation_ai_generates_response():
    engine = AIEngine(FakeProvider())
    context = ConversationContext()

    conversation = ConversationAI(engine, context)

    result = conversation.respond("Olá, Wattson")

    assert result == "resposta: Olá, Wattson"


def test_conversation_ai_uses_ai_engine():
    class SpyEngine:
        def __init__(self):
            self.received_message = None

        def generate(self, prompt: str) -> str:
            self.received_message = prompt
            return "resposta do engine"

    engine = SpyEngine()
    context = ConversationContext()

    conversation = ConversationAI(engine, context)

    result = conversation.respond("Teste de integração")

    assert engine.received_message == "Teste de integração"
    assert result == "resposta do engine"
