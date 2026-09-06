class WattsonCore:
    """
    Núcleo principal do Wattson.

    Responsabilidades desta versão:
    - receber uma mensagem;
    - enviar a mensagem para um provedor de IA;
    - retornar a resposta.

    O Core não conhece qual IA está sendo utilizada.
    """

    def __init__(self, ai_provider):
        self.name = "Wattson"
        self.version = "0.2.0"

        self.ai_provider = ai_provider

    def think(self, message: str) -> str:
        """
        Processa uma entrada através do provedor de IA.
        """

        if not message or not message.strip():
            return "Não recebi nenhuma entrada."

        response = self.ai_provider.generate(message)

        return response
