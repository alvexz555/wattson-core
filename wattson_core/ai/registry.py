import importlib


def load(name: str):
    try:
        return importlib.import_module(
            f"wattson_core.ai.providers.{name}"
        )
    except Exception:
        return None
