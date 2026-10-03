from wattson_core.terminal import WattsonTerminal


class FakeTerminal:
    def __init__(self):
        self.messages = []

    def process(self, message):
        self.messages.append(message)
        return f"Resposta para: {message}"


def test_terminal_loop_stops_on_exit():
    terminal = FakeTerminal()

    inputs = iter([
        "Olá, Wattson.",
        "Como você está?",
        "sair",
    ])

    outputs = []

    while True:
        message = next(inputs)

        if message.lower() == "sair":
            break

        outputs.append(terminal.process(message))

    assert terminal.messages == [
        "Olá, Wattson.",
        "Como você está?",
    ]

    assert outputs == [
        "Resposta para: Olá, Wattson.",
        "Resposta para: Como você está?",
    ]
