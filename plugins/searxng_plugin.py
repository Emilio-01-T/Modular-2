from plugins.plugin_base import PluginBase
import requests
import logging

logger = logging.getLogger("modular-2")

class SearXNGPlugin(PluginBase):
    name = "searxng_search"
    description = "Plugin per ricerca web tramite motore SearXNG self-hosted o pubblico."

    def __init__(self, base_url="https://searxng.example.com"):
        self.base_url = base_url.rstrip('/')

    def run(self, query):
        search_url = f"{self.base_url}/search"
        params = {
            "q": query,
            "format": "json"
        }
        try:
            response = requests.get(search_url, params=params)
            response.raise_for_status()
            results = response.json().get("results", [])
            snippets = [result.get("content", "") for result in results]
            return "\\n".join(snippets)
        except Exception as e:
            logger.error(f"[Plugin] Errore ricerca SearXNG: {e}")
            return "Errore nella ricerca SearXNG."
