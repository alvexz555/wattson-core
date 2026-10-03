from wattson_core.ai.context import ConversationContext
from wattson_core.ai.conversation import ConversationAI
from wattson_core.ai.engine import AIEngine
from wattson_core.ai.providers.ollama import WattsonProvider


def test_conversation_ai_uses_real_dolphin():
    provider = WattsonProvider()
    engine = AIEngine(provider)
    context = ConversationContext()

    conversation = ConversationAI(engine, context)

    response = conversation.respond(
        "Olá, Wattson. Diga apenas que recebeu esta mensagem."
    )

    assert isinstance(response, str)
    assert response.strip()

    assert context.messages[0] == (
        "Olá, Wattson. Diga apenas que recebeu esta mensagem."
    )

    assert context.messages[-1] == response
