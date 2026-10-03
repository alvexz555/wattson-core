from wattson_core.core.orchestrator import Orchestrator


class FakeDiagnosticTool:
    def __init__(self):
        self.called = False

    def run(self):
        self.called = True
        return {
            "status": "healthy",
            "errors": [],
        }


class FakeConversation:
    def respond(self, message):
        return "Solicitação processada."


def test_diagnostic_request_triggers_diagnostic_tool():
    diagnostic_tool = FakeDiagnosticTool()

    orchestrator = Orchestrator(
        conversation=FakeConversation(),
        diagnostic_tool=diagnostic_tool,
    )

    result = orchestrator.handle(
        "Wattson, confira os erros nesse projeto."
    )

    assert diagnostic_tool.called is True
    assert result is not None
