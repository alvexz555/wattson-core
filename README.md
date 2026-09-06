flowchart TD

    UI["Interface<br>index.html"]
    SERVER["Servidor<br>server.py"]
    CORE["Wattson Core<br>main.py"]
    OPENAI["OpenAI API"]

    UI --> SERVER
    SERVER --> CORE
    CORE --> OPENAI
