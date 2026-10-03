from wattson_core.core.orchestrator import Orchestrator


class FakeConversation:
    def respond(self, message):
        return "Resposta da conversa."


class FakeSearchTool:
    def __init__(self):
        self.called = False
        self.query = None

    def search(self, query):
        self.called = True
        self.query = query
        return [
            {
                "title": "Resultado de teste",
                "url": "https://example.com",
                "content": "Conteúdo de teste",
            }
        ]


def test_orchestrator_routes_search_request_to_search_tool():
    conversation = FakeConversation()
    search_tool = FakeSearchTool()

    orchestrator = Orchestrator(
        conversation,
        search_tool=search_tool,
    )

    result = orchestrator.handle("Pesquise Raspberry Pi")

    assert search_tool.called is True
    assert search_tool.query == "Pesquise Raspberry Pi"
