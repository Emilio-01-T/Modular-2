import unittest
import asyncio
import sys
import os
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from managers.advanced_agent_manager import AdvancedAgentManager

class DummyAgent:
    def __init__(self, name):
        self.name = name
        self.run = MagicMock(return_value=f"result from {name}")

class TestAdvancedAgentManager(unittest.TestCase):
    def setUp(self):
        self.agent_configs = [
            MagicMock(name="agent1", spec=['name', 'type', 'tools']),
            MagicMock(name="agent2", spec=['name', 'type', 'tools'])
        ]
        self.agent_configs[0].name = "agent1"
        self.agent_configs[0].type = "simple"
        self.agent_configs[0].tools = []
        self.agent_configs[1].name = "agent2"
        self.agent_configs[1].type = "simple"
        self.agent_configs[1].tools = []
        self.llm = MagicMock()
        self.manager = AdvancedAgentManager(self.agent_configs, self.llm)
        # Replace agents with dummy agents
        self.manager.agents = [DummyAgent("agent1"), DummyAgent("agent2")]

    def test_orchestrate(self):
        inputs = {"agent1": "input1", "agent2": "input2"}
        results = asyncio.run(self.manager.orchestrate(inputs))
        self.assertEqual(results["agent1"], "result from agent1")
        self.assertEqual(results["agent2"], "result from agent2")
        for agent in self.manager.agents:
            agent.run.assert_called_once()

    def test_run(self):
        inputs = {"agent1": "input1", "agent2": "input2"}
        results = self.manager.run(inputs)
        self.assertEqual(results["agent1"], "result from agent1")
        self.assertEqual(results["agent2"], "result from agent2")

if __name__ == "__main__":
    unittest.main()
