class WattsonTerminal:
    def __init__(self, orchestrator):
        self.orchestrator = orchestrator

    def process(self, message: str) -> str:
        return self.orchestrator.handle(message)
