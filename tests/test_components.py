import unittest
import sys
import os

# Aggiungo la root del progetto al path per importare i moduli
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from tools.math_tool import MathTool
from core.memory import ConversationMemory
from agents.simple_agent import SimpleAgent
from llm_providers.ollama_llm import OllamaLLM
from unittest.mock import MagicMock

class TestMathTool(unittest.TestCase):
    def setUp(self):
        self.tool = MathTool()

    def test_run_valid_expression(self):
        result = self.tool.run("2+2")
        self.assertEqual(result, 4)

    def test_run_invalid_expression(self):
        result = self.tool.run("2+/2")
        self.assertTrue("Errore nel calcolo" in result)

class TestConversationMemory(unittest.TestCase):
    def setUp(self):
        self.memory = ConversationMemory()

    def test_save_and_load(self):
        session_id = "test_session"
        data = "test data"
        self.memory.save(session_id, data)
        loaded = self.memory.load(session_id)
        self.assertIn(data, loaded)

class TestSimpleAgent(unittest.TestCase):
    def setUp(self):
        self.llm = MagicMock()
        self.llm.generate.return_value = "response"
        self.tool = MathTool()
        self.agent = SimpleAgent(llm=self.llm, tools=[self.tool], name="TestAgent")

    def test_run(self):
        response = self.agent.run("2+2")
        self.llm.generate.assert_called_once()
        self.assertEqual(response, "response")

class TestOllamaLLM(unittest.TestCase):
    def setUp(self):
        # Mock requests.post to avoid real HTTP calls
        import llm_providers.ollama_llm as ollama_module
        self.ollama = OllamaLLM(model="test-model", endpoint="http://test-endpoint")
        self.requests_post_original = ollama_module.requests.post
        ollama_module.requests.post = MagicMock()

    def tearDown(self):
        import llm_providers.ollama_llm as ollama_module
        ollama_module.requests.post = self.requests_post_original

    def test_generate_success(self):
        import llm_providers.ollama_llm as ollama_module
        mock_response = MagicMock()
        mock_response.json.return_value = {"response": "test response"}
        mock_response.raise_for_status = MagicMock()
        ollama_module.requests.post.return_value = mock_response

        response = self.ollama.generate("prompt")
        self.assertEqual(response, "test response")

    def test_generate_failure(self):
        import llm_providers.ollama_llm as ollama_module
        ollama_module.requests.post.side_effect = Exception("fail")

        with self.assertRaises(Exception):
            self.ollama.generate("prompt")

if __name__ == "__main__":
    unittest.main()
