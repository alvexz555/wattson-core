from wattson_core.ai.conversation import ConversationAI
from wattson_core.ai.context import ConversationContext


class FakeEngine:
    def __init__(self):
        self.prompts = []

    def generate(self, prompt: str) -> str:
        self.prompts.append(prompt)
        return "resposta"


def test_conversation_ai_includes_previous_context():
    engine = FakeEngine()
    context = ConversationContext()

    context.add("Meu nome é A.RISE.")

    conversation = ConversationAI(engine, context)

    conversation.respond("Qual é o meu nome?")

    assert "Meu nome é A.RISE." in engine.prompts[0]
    assert "Qual é o meu nome?" in engine.prompts[0]
