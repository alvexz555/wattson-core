from wattson_core.core.orchestrator import Orchestrator


class FakeConversation:
    def __init__(self):
        self.received = None

    def respond(self, message):
        self.received = message
        return "Resposta."


class FakeSearchTool:
    def search(self, query):
        return [
            {
                "title": f"Resultado {i}",
                "url": f"https://example.com/{i}",
                "content": f"Conteúdo {i}",
            }
            for i in range(1, 29)
        ]


def test_search_context_uses_only_first_five_results():
    conversation = FakeConversation()
    search_tool = FakeSearchTool()

    orchestrator = Orchestrator(
        conversation,
        search_tool=search_tool,
    )

    orchestrator.handle("Pesquise Raspberry Pi")

    prompt = conversation.received

    assert "Resultado 1" in prompt
    assert "Resultado 5" in prompt
    assert "Resultado 6" not in prompt
    assert "Resultado 28" not in prompt
