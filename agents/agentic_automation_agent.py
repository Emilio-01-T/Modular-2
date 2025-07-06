import logging
from typing import List, Dict, Any, Callable

logger = logging.getLogger("modular-2")

class AgenticAutomationAgent:
    def __init__(self, llm_callable: Callable[[str], str], tools: Dict[str, Callable[[Any], Any]], name="agentic_automation_agent"):
        """
        llm_callable: funzione che prende un prompt testuale e ritorna la risposta LLM
        tools: dizionario di strumenti disponibili, chiave nome strumento, valore funzione esecutrice
        """
        self.llm_callable = llm_callable
        self.tools = tools
        self.name = name

    def run(self, task_description: str):
        logger.info(f"[AgenticAutomationAgent] Ricevuto task: {task_description}")
        # Logica semplificata di agente agentic multi-step:
        # 1. Usa LLM per decidere quale tool usare e con quali input
        # 2. Esegue il tool scelto
        # 3. Usa LLM per decidere se terminare o continuare con altri tool
        # 4. Ripete fino a completamento

        intermediate_steps = []
        current_input = task_description
        max_steps = 5

        for step in range(max_steps):
            prompt = self._build_prompt(current_input, intermediate_steps)
            llm_output = self.llm_callable(prompt)
            logger.info(f"[AgenticAutomationAgent] LLM output step {step}: {llm_output}")

            tool_name, tool_input = self._parse_llm_output(llm_output)
            if tool_name not in self.tools:
                logger.warning(f"[AgenticAutomationAgent] Tool '{tool_name}' non trovato. Termino.")
                break

            tool_func = self.tools[tool_name]
            tool_result = tool_func(tool_input)
            logger.info(f"[AgenticAutomationAgent] Risultato tool '{tool_name}': {tool_result}")

            intermediate_steps.append((tool_name, tool_input, tool_result))

            if self._should_stop(llm_output):
                logger.info("[AgenticAutomationAgent] Condizione di stop raggiunta.")
                break

            current_input = tool_result

        final_output = intermediate_steps[-1][2] if intermediate_steps else "Nessun risultato"
        logger.info(f"[AgenticAutomationAgent] Output finale: {final_output}")
        return final_output

    def _build_prompt(self, current_input: str, intermediate_steps: List):
        # Costruisce il prompt per LLM includendo contesto e risultati precedenti
        context = "\\n".join([f"Step: {i}, Tool: {step[0]}, Input: {step[1]}, Output: {step[2]}" for i, step in enumerate(intermediate_steps)])
        prompt = f"Sei un agente AI che esegue task multi-step. Input corrente: {current_input}\\nStorico passi:\\n{context}\\nDecidi il prossimo tool da usare e il suo input nel formato 'Tool: <nome_tool>, Input: <input>'. Se vuoi terminare, scrivi 'Stop'."
        return prompt

    def _parse_llm_output(self, llm_output: str):
        # Parsing semplice per estrarre tool e input dal testo LLM
        # Esempio output: "Tool: math, Input: 2+2"
        if "Stop" in llm_output:
            return None, None
        try:
            parts = llm_output.split(",")
            tool_part = parts[0].strip()
            input_part = parts[1].strip()
            tool_name = tool_part.split(":")[1].strip()
            tool_input = input_part.split(":")[1].strip()
            return tool_name, tool_input
        except Exception as e:
            logger.error(f"[AgenticAutomationAgent] Errore parsing output LLM: {e}")
            return None, None

    def _should_stop(self, llm_output: str):
        return "Stop" in llm_output
