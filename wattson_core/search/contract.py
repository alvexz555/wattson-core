import json
from urllib.parse import urlencode
from urllib.request import urlopen


class SearchTool:
    BASE_URL = "http://192.168.1.107:8080/search"

    def search(self, query: str):
        params = urlencode({
            "q": query,
            "format": "json",
        })

        with urlopen(f"{self.BASE_URL}?{params}", timeout=10) as response:
            data = json.load(response)

        return data["results"]
