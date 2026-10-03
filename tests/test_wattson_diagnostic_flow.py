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
        return "Resposta normal."


def test_wattson_can_execute_diagnostic_task():
    diagnostic_tool = FakeDiagnosticTool()

    orchestrator = Orchestrator(
        conversation=FakeConversation(),
        diagnostic_tool=diagnostic_tool,
    )

    response = orchestrator.handle(
        "Wattson, confira os erros nesse projeto."
    )

    assert diagnostic_tool.called is True
    assert "healthy" in response
    assert "errors" in response
