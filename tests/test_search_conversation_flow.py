from wattson_core.core.orchestrator import Orchestrator


class FakeConversation:
    def __init__(self):
        self.received = None

    def respond(self, message):
        self.received = message
        return "Resposta baseada na pesquisa."


class FakeSearchTool:
    def search(self, query):
        return [
            {
                "title": "Raspberry Pi",
                "url": "https://example.com",
                "content": "Computador de placa única.",
            }
        ]


def test_search_results_are_sent_to_conversation():
    conversation = FakeConversation()
    search_tool = FakeSearchTool()

    orchestrator = Orchestrator(
        conversation,
        search_tool=search_tool,
    )

    result = orchestrator.handle("Pesquise Raspberry Pi")

    assert result == "Resposta baseada na pesquisa."
    assert conversation.received is not None
    assert "Raspberry Pi" in conversation.received
    assert "Computador de placa única." in conversation.received
