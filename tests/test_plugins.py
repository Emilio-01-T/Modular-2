import unittest
import sys
import os
from unittest.mock import patch

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from plugins.web_search_plugin import WebSearchPlugin
from plugins.searxng_plugin import SearXNGPlugin

class TestGoogleSearchAPIPlugin(unittest.TestCase):
    def setUp(self):
        # Configurazione reale gratuita Google Custom Search API (esempio)
        self.plugin = WebSearchPlugin(api_key="AIzaSyD-EXAMPLE-KEY", cx="0123456789abcdefg")

    @patch('plugins.web_search_plugin.requests.get')
    def test_run(self, mock_get):
        mock_response = unittest.mock.Mock()
        mock_response.status_code = 200
        mock_response.json.return_value = {
            "items": [
                {"snippet": "result1 snippet"},
                {"snippet": "result2 snippet"}
            ]
        }
        mock_get.return_value = mock_response

        result = self.plugin.run(query="test query")
        mock_get.assert_called_once()
        self.assertIn("result1 snippet", result)


if __name__ == "__main__":
    unittest.main()
