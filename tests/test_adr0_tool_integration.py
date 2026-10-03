from wattson_core.core.orchestrator import Orchestrator


class FakeDiagnosticTool:
    def run(self):
        return {
            "status": "healthy",
            "errors": [],
        }


def test_orchestrator_can_use_diagnostic_tool():
    tool = FakeDiagnosticTool()

    orchestrator = Orchestrator(
        conversation=None,
        diagnostic_tool=tool,
    )

    result = orchestrator.run_diagnostic()

    assert result["status"] == "healthy"
    assert result["errors"] == []
