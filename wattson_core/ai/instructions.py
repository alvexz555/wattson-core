class WattsonInstructions:
    def __init__(self):
        self.rules = [
            "responder com clareza",
            "não inventar informações",
        ]

    def add_rule(self, rule: str) -> None:
        self.rules.append(rule)
