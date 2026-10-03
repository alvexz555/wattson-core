from wattson_core.core.orchestrator import Orchestrator


def test_orchestrator_delegates_message_to_conversation():
    class FakeConversation:
        def __init__(self):
            self.received_message = None

        def respond(self, message: str) -> str:
            self.received_message = message
            return "resposta da conversa"

    conversation = FakeConversation()
    orchestrator = Orchestrator(conversation)

    result = orchestrator.handle("Olá, Wattson")

    assert conversation.received_message == "Olá, Wattson"
    assert result == "resposta da conversa"
