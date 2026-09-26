from wattson_core.search.contract import SearchTool


def test_search_tool_returns_results():
    tool = SearchTool()

    results = tool.search("Raspberry Pi")

    assert results


def test_search_tool_returns_list():
    tool = SearchTool()

    results = tool.search("Linux")

    assert isinstance(results, list)
    assert results
def test_search_results_have_expected_fields():
    tool = SearchTool()

    results = tool.search("Linux")

    assert results

    for result in results[:5]:
        assert isinstance(result, dict)
        assert "title" in result
        assert "url" in result
        assert "content" in result
import pytest
from urllib.error import URLError


def test_search_tool_raises_error_when_server_unavailable():
    tool = SearchTool()

    tool.BASE_URL = "http://192.168.1.107:9999/search"

    with pytest.raises(URLError):
        tool.search("Linux")
def test_search_tool_raises_error_on_timeout():
    tool = SearchTool()

    tool.BASE_URL = "http://10.255.255.1:8080/search"

    with pytest.raises(URLError):
        tool.search("Linux")
