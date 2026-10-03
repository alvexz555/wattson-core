from wattson_core.ai.context import ConversationContext
from wattson_core.ai.conversation import ConversationAI
from wattson_core.ai.engine import AIEngine
from wattson_core.ai.providers.ollama import WattsonProvider
from wattson_core.core.orchestrator import Orchestrator
from wattson_core.terminal import WattsonTerminal


def test_terminal_reaches_real_dolphin():
    provider = WattsonProvider()
    engine = AIEngine(provider)
    context = ConversationContext()
    conversation = ConversationAI(engine, context)
    orchestrator = Orchestrator(conversation)
    terminal = WattsonTerminal(orchestrator)

    response = terminal.process(
        "Olá, Wattson. Responda apenas: terminal conectado ao Dolphin."
    )

    assert isinstance(response, str)
    assert response.strip()

    assert context.messages[0] == (
        "Olá, Wattson. Responda apenas: terminal conectado ao Dolphin."
    )

    assert context.messages[-1] == response
