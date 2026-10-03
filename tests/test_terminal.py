from wattson_core.terminal import WattsonTerminal


class FakeOrchestrator:
    def __init__(self):
        self.received = []

    def handle(self, message):
        self.received.append(message)
        return "Resposta do Wattson."


def test_terminal_processes_user_message():
    orchestrator = FakeOrchestrator()
    terminal = WattsonTerminal(orchestrator)

    response = terminal.process("Olá, Wattson.")

    assert orchestrator.received == ["Olá, Wattson."]
    assert response == "Resposta do Wattson."
