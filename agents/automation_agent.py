from agents.simple_agent import SimpleAgent
import logging
from typing import Callable, Dict, Any

logger = logging.getLogger("modular-2")

class AutomationAgent(SimpleAgent):
    def __init__(self, llm, tools=None, name="automation_agent", plugin=None):
        super().__init__(llm=llm, tools=tools or [], name=name)
        self.plugin = plugin

    def run(self, task_description: str):
        logger.info(f"[AutomationAgent] Ricevuto task: {task_description}")
        if self.plugin:
            # Esempio di esecuzione plugin con task description
            result = self.plugin.run(task_description)
            logger.info(f"[AutomationAgent] Risultato plugin: {result}")
            return result
        else:
            logger.warning("[AutomationAgent] Nessun plugin di automazione configurato.")
            return "Nessun plugin di automazione configurato."
