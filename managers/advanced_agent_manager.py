"""
advanced_agent_manager.py - Orchestrazione avanzata multi-agent

- Gestisce la comunicazione, scheduling e coordinamento tra più agenti.
- Supporta workflow distribuiti e scenari complessi.
"""

import asyncio
import logging
from managers.agent_manager import create_agents

logger = logging.getLogger(__name__)

class AdvancedAgentManager:
    def __init__(self, agent_configs, llm):
        self.agents = create_agents(agent_configs, llm)
        self.task_queue = asyncio.Queue()
        self.results = {}

    async def run_agent(self, agent, input_data):
        logger.info(f"Avvio agente {agent.name} con input: {input_data}")
        result = await asyncio.to_thread(agent.run, input_data)
        logger.info(f"Agente {agent.name} ha prodotto risultato: {result}")
        return result

    async def orchestrate(self, inputs):
        # inputs: dict {agent_name: input_data}
        tasks = []
        for agent in self.agents:
            input_data = inputs.get(agent.name, "")
            tasks.append(self.run_agent(agent, input_data))
        results = await asyncio.gather(*tasks)
        for agent, res in zip(self.agents, results):
            self.results[agent.name] = res
        return self.results

    def run(self, inputs):
        return asyncio.run(self.orchestrate(inputs))
