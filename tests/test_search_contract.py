import json

from wattson_core.search.contract import SearchTool


class FakeResponse:
    def __init__(self, data):
        self.data = data

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        pass

    def read(self):
        return json.dumps(self.data).encode()


def test_search_tool_extracts_results_from_json(monkeypatch):
    expected_results = [
        {
            "title": "Resultado de teste",
            "url": "https://example.com",
            "content": "Conteúdo de teste",
        }
    ]

    def fake_urlopen(url, timeout):
        return FakeResponse({"results": expected_results})

    monkeypatch.setattr(
        "wattson_core.search.contract.urlopen",
        fake_urlopen,
    )

    tool = SearchTool()

    results = tool.search("teste")

    assert results == expected_results
