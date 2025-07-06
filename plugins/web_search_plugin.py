from plugins.plugin_base import PluginBase
import requests
import logging

logger = logging.getLogger("modular-2")

class WebSearchPlugin(PluginBase):
    name = "web_search"
    description = "Plugin per ricerca web tramite API esterne (es. Google Custom Search)."

    def __init__(self, api_key, cx):
        self.api_key = api_key
        self.cx = cx

    def run(self, query):
        url = "https://www.googleapis.com/customsearch/v1"
        params = {
            "key": self.api_key,
            "cx": self.cx,
            "q": query
        }
        try:
            response = requests.get(url, params=params)
            response.raise_for_status()
            results = response.json().get("items", [])
            snippets = [item.get("snippet", "") for item in results]
            return "\\n".join(snippets)
        except Exception as e:
            logger.error(f"[Plugin] Errore ricerca web: {e}")
            return "Errore nella ricerca web."
