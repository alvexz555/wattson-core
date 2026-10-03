from .errors import AIProviderError


class AIEngine:
    def __init__(self, provider):
        self.provider = provider

    def generate(self, prompt: str) -> str:
        if not isinstance(prompt, str):
            raise TypeError("Prompt deve ser uma string.")

        try:
            return self.provider.generate(prompt)
        except Exception as error:
            raise AIProviderError(str(error)) from error
