"""
Agentic Automation Agent implementation for modular-2 framework.
Advanced autonomous agent capable of multi-step task execution.
"""
import logging
from typing import List, Dict, Any, Optional
import json
import re

logger = logging.getLogger(__name__)

class AgenticAutomationAgent:
    """
    Advanced autonomous agent that can break down complex tasks into steps
    and execute them using available tools and reasoning.
    """
    
    def __init__(self, name: str, llm, tools: Optional[List] = None, 
                 system_prompt: str = "", max_iterations: int = 5, config: Dict = None):
        """
        Initialize the agentic automation agent.
        
        Args:
            name: Agent name
            llm: LLM provider instance
            tools: List of tool instances
            system_prompt: System prompt for the agent
            max_iterations: Maximum number of reasoning iterations
            config: Additional configuration
        """
        self.name = name
        self.llm = llm
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.max_iterations = max_iterations
        self.config = config or {}
        
        # Create tool mapping
        self.tool_map = {tool.__class__.__name__.lower(): tool for tool in self.tools}
        
        # Task execution state
        self.execution_history = []
        self.current_context = {}
        
        logger.info(f"🤖 Agente autonomo '{self.name}' inizializzato con {len(self.tools)} tool(s)")
        logger.info(f"🎯 Max iterazioni: {self.max_iterations}")
    
    def run(self, input_data: Dict[str, Any]) -> str:
        """
        Execute autonomous task with multi-step reasoning.
        
        Args:
            input_data: Input data containing task description
            
        Returns:
            Final result after autonomous execution
        """
        try:
            task = input_data.get("prompt", "")
            
            # Reset execution state
            self.execution_history = []
            self.current_context = {"original_task": task}
            
            logger.info(f"🚀 Avvio task autonomo per '{self.name}': {task}")
            
            # Create initial plan
            plan = self._create_task_plan(task)
            self.current_context["plan"] = plan
            
            # Execute the plan
            result = self._execute_plan(plan)
            
            # Generate final summary
            final_result = self._generate_final_summary(result)
            
            logger.info(f"✅ Task autonomo completato per '{self.name}'")
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione autonoma per '{self.name}': {e}")
            return f"Errore nell'esecuzione autonoma: {str(e)}"
    
    def _create_task_plan(self, task: str) -> List[Dict]:
        """Create a step-by-step plan for the given task."""
        planning_prompt = f"""
{self.system_prompt}

Sei un agente autonomo che deve creare un piano dettagliato per completare il seguente task.

Task: {task}

Tools disponibili: {', '.join([tool.__class__.__name__ for tool in self.tools])}

Crea un piano step-by-step in formato JSON con questa struttura:
[
  {{
    "step": 1,
    "action": "analyze|tool|reasoning",
    "description": "Descrizione dello step",
    "tool": "nome_tool_se_necessario",
    "expected_output": "cosa ci aspettiamo"
  }}
]

Rispondi SOLO con il JSON del piano:"""
        
        try:
            response = self.llm.generate(planning_prompt)
            
            # Extract JSON from response
            json_match = re.search(r'\[.*\]', response, re.DOTALL)
            if json_match:
                plan_json = json_match.group()
                plan = json.loads(plan_json)
                logger.info(f"📋 Piano creato con {len(plan)} step per '{self.name}'")
                return plan
            else:
                # Fallback to simple plan
                logger.warning(f"⚠️ Impossibile parsare il piano JSON, uso piano semplice")
                return self._create_simple_plan(task)
                
        except Exception as e:
            logger.warning(f"⚠️ Errore nella creazione del piano: {e}, uso piano semplice")
            return self._create_simple_plan(task)
    
    def _create_simple_plan(self, task: str) -> List[Dict]:
        """Create a simple fallback plan."""
        return [
            {
                "step": 1,
                "action": "analyze",
                "description": f"Analizza il task: {task}",
                "tool": None,
                "expected_output": "Comprensione del task"
            },
            {
                "step": 2,
                "action": "reasoning",
                "description": "Ragiona sulla soluzione migliore",
                "tool": None,
                "expected_output": "Strategia di soluzione"
            },
            {
                "step": 3,
                "action": "tool",
                "description": "Esegui azioni necessarie con i tool",
                "tool": "auto",
                "expected_output": "Risultato dell'azione"
            }
        ]
    
    def _execute_plan(self, plan: List[Dict]) -> str:
        """Execute the created plan step by step."""
        results = []
        
        for step_info in plan:
            if len(self.execution_history) >= self.max_iterations:
                logger.warning(f"⚠️ Raggiunto limite iterazioni ({self.max_iterations}) per '{self.name}'")
                break
            
            step_result = self._execute_step(step_info)
            results.append(step_result)
            
            # Update context with step result
            self.current_context[f"step_{step_info['step']}_result"] = step_result
            
            # Add to execution history
            self.execution_history.append({
                "step": step_info,
                "result": step_result,
                "timestamp": "now"  # In a real implementation, use actual timestamp
            })
        
        return "\n\n".join(results)
    
    def _execute_step(self, step_info: Dict) -> str:
        """Execute a single step of the plan."""
        step_num = step_info.get("step", 0)
        action = step_info.get("action", "reasoning")
        description = step_info.get("description", "")
        tool_name = step_info.get("tool")
        
        logger.info(f"🔄 Esecuzione step {step_num} per '{self.name}': {description}")
        
        try:
            if action == "tool" and tool_name:
                return self._execute_tool_step(step_info)
            elif action == "analyze":
                return self._execute_analysis_step(step_info)
            elif action == "reasoning":
                return self._execute_reasoning_step(step_info)
            else:
                return self._execute_generic_step(step_info)
                
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione step {step_num}: {e}")
            return f"Errore step {step_num}: {str(e)}"
    
    def _execute_tool_step(self, step_info: Dict) -> str:
        """Execute a step that involves using a tool."""
        tool_name = step_info.get("tool", "").lower()
        description = step_info.get("description", "")
        
        # Auto-select tool if needed
        if tool_name == "auto":
            selected_tool = self._auto_select_tool(description)
        else:
            selected_tool = self.tool_map.get(tool_name)
        
        if selected_tool:
            try:
                # Prepare tool input based on current context
                tool_input = self._prepare_tool_input(selected_tool, step_info)
                result = selected_tool.run(tool_input)
                
                logger.info(f"🔧 Tool '{selected_tool.__class__.__name__}' eseguito con successo")
                return f"Tool {selected_tool.__class__.__name__} result: {result}"
                
            except Exception as e:
                logger.error(f"❌ Errore nell'esecuzione tool: {e}")
                return f"Errore tool: {str(e)}"
        else:
            return f"Tool '{tool_name}' non trovato, procedo con ragionamento"
    
    def _execute_analysis_step(self, step_info: Dict) -> str:
        """Execute an analysis step."""
        description = step_info.get("description", "")
        
        analysis_prompt = f"""
Analizza il seguente task nel contesto del piano di esecuzione:

Task originale: {self.current_context.get('original_task', '')}
Step corrente: {description}

Contesto precedente:
{self._get_context_summary()}

Fornisci un'analisi dettagliata e identifica i prossimi passi necessari:"""
        
        try:
            result = self.llm.generate(analysis_prompt)
            return f"Analisi: {result}"
        except Exception as e:
            return f"Errore nell'analisi: {str(e)}"
    
    def _execute_reasoning_step(self, step_info: Dict) -> str:
        """Execute a reasoning step."""
        description = step_info.get("description", "")
        
        reasoning_prompt = f"""
Ragiona sulla migliore strategia per completare il task:

Task: {self.current_context.get('original_task', '')}
Step: {description}

Contesto ed esecuzione precedente:
{self._get_context_summary()}

Fornisci il tuo ragionamento e la strategia da seguire:"""
        
        try:
            result = self.llm.generate(reasoning_prompt)
            return f"Ragionamento: {result}"
        except Exception as e:
            return f"Errore nel ragionamento: {str(e)}"
    
    def _execute_generic_step(self, step_info: Dict) -> str:
        """Execute a generic step."""
        description = step_info.get("description", "")
        
        generic_prompt = f"""
Esegui il seguente step del piano:

{description}

Contesto:
{self._get_context_summary()}

Fornisci il risultato dell'esecuzione:"""
        
        try:
            result = self.llm.generate(generic_prompt)
            return f"Risultato: {result}"
        except Exception as e:
            return f"Errore nell'esecuzione: {str(e)}"
    
    def _auto_select_tool(self, description: str) -> Optional[Any]:
        """Automatically select the most appropriate tool."""
        if not self.tools:
            return None
        
        # Simple keyword-based selection
        description_lower = description.lower()
        
        for tool in self.tools:
            tool_name = tool.__class__.__name__.lower()
            if "math" in tool_name and any(kw in description_lower for kw in ["calcola", "math", "+", "-", "*", "/"]):
                return tool
            elif "search" in tool_name and any(kw in description_lower for kw in ["cerca", "search", "trova"]):
                return tool
            elif "file" in tool_name and any(kw in description_lower for kw in ["file", "documento", "leggi"]):
                return tool
        
        # Return first tool as fallback
        return self.tools[0] if self.tools else None
    
    def _prepare_tool_input(self, tool, step_info: Dict) -> Dict:
        """Prepare input for tool execution."""
        # Basic input preparation - can be enhanced based on tool requirements
        return {
            "prompt": step_info.get("description", ""),
            "context": self.current_context,
            "step_info": step_info
        }
    
    def _get_context_summary(self) -> str:
        """Get a summary of the current execution context."""
        summary_parts = []
        
        if self.execution_history:
            summary_parts.append("Esecuzione precedente:")
            for i, entry in enumerate(self.execution_history[-3:]):  # Last 3 steps
                step_desc = entry["step"].get("description", "")
                result = entry["result"][:100] + "..." if len(entry["result"]) > 100 else entry["result"]
                summary_parts.append(f"  Step {entry['step'].get('step', i+1)}: {step_desc} -> {result}")
        
        return "\n".join(summary_parts) if summary_parts else "Nessun contesto precedente"
    
    def _generate_final_summary(self, execution_result: str) -> str:
        """Generate a final summary of the autonomous execution."""
        summary_prompt = f"""
Genera un riassunto finale dell'esecuzione autonoma del task:

Task originale: {self.current_context.get('original_task', '')}

Risultati dell'esecuzione:
{execution_result}

Cronologia completa:
{self._get_context_summary()}

Fornisci un riassunto conciso e il risultato finale:"""
        
        try:
            summary = self.llm.generate(summary_prompt)
            
            final_result = f"""
=== ESECUZIONE AUTONOMA COMPLETATA ===

Task: {self.current_context.get('original_task', '')}
Agente: {self.name}
Step eseguiti: {len(self.execution_history)}

{summary}

=== DETTAGLI ESECUZIONE ===
{execution_result}
"""
            return final_result
            
        except Exception as e:
            logger.error(f"❌ Errore nella generazione del riassunto finale: {e}")
            return f"Task completato con errori nel riassunto: {execution_result}"