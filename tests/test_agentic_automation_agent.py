import unittest
from unittest.mock import MagicMock

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))
from agents.agentic_automation_agent import AgenticAutomationAgent

class TestAgenticAutomationAgent(unittest.TestCase):
    def setUp(self):
        # Mock LLM callable that decides tool and input based on prompt
        def mock_llm(prompt):
            if "Step: 0" not in prompt:
                return "Tool: math, Input: 2+2"
            else:
                return "Stop"

        # Mock tools dictionary with a math tool
        self.tools = {
            "math": lambda expr: eval(expr)
        }

        self.agent = AgenticAutomationAgent(llm_callable=mock_llm, tools=self.tools)

    def test_run(self):
        task_description = "Calcola 2+2"
        result = self.agent.run(task_description)
        self.assertEqual(result, 4)

if __name__ == "__main__":
    unittest.main()
