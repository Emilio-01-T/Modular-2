"""
Tool Agent implementation for modular-2 framework.
Agent specialized in using tools effectively.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class ToolAgent:
    """
    Agent specialized in using tools to accomplish tasks.
    """
    
    def __init__(self, name: str, llm, tools: Optional[List] = None, 
                 system_prompt: str = "", config: Dict = None):
        """
        Initialize the tool agent.
        
        Args:
            name: Agent name
            llm: LLM provider instance
            tools: List of tool instances
            system_prompt: System prompt for the agent
            config: Additional configuration
        """
        self.name = name
        self.llm = llm
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.config = config or {}
        
        # Create tool mapping for easy access
        self.tool_map = {tool.__class__.__name__.lower(): tool for tool in self.tools}
        
        logger.info(f"🔧 Tool agente '{self.name}' inizializzato con {len(self.tools)} tool(s)")
    
    def run(self, input_data: Dict[str, Any]) -> str:
        """
        Execute the agent with focus on tool usage.
        
        Args:
            input_data: Input data containing prompt and other parameters
            
        Returns:
            Agent response as string
        """
        try:
            prompt = input_data.get("prompt", "")
            
            # Prepare the full prompt with tool information
            full_prompt = self._prepare_tool_prompt(prompt)
            
            # Analyze which tools to use
            tools_to_use = self._analyze_tool_needs(prompt)
            
            if tools_to_use:
                return self._execute_with_tools(full_prompt, input_data, tools_to_use)
            else:
                return self._execute_without_tools(full_prompt)
                
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione del tool agente '{self.name}': {e}")
            return f"Errore: {str(e)}"
    
    def _prepare_tool_prompt(self, user_prompt: str) -> str:
        """Prepare prompt with detailed tool information."""
        tool_descriptions = []
        
        for tool in self.tools:
            tool_name = tool.__class__.__name__
            tool_desc = getattr(tool, 'description', f"Tool: {tool_name}")
            tool_descriptions.append(f"- {tool_name}: {tool_desc}")
        
        tool_info = ""
        if tool_descriptions:
            tool_info = f"\n\nTool disponibili:\n" + "\n".join(tool_descriptions)
            tool_info += "\n\nUsa i tool quando necessario per fornire risposte accurate."
        
        if self.system_prompt:
            return f"{self.system_prompt}{tool_info}\n\nUser: {user_prompt}"
        return f"Sei un assistente che può usare vari tool per aiutare l'utente.{tool_info}\n\nUser: {user_prompt}"
    
    def _analyze_tool_needs(self, prompt: str) -> List:
        """Analyze which tools are needed for the given prompt."""
        needed_tools = []
        prompt_lower = prompt.lower()
        
        for tool in self.tools:
            # Check if tool has a should_use method
            if hasattr(tool, 'should_use') and callable(tool.should_use):
                try:
                    if tool.should_use(prompt):
                        needed_tools.append(tool)
                        logger.debug(f"🎯 Tool '{tool.__class__.__name__}' selezionato per il prompt")
                except Exception as e:
                    logger.warning(f"⚠️ Errore nel controllo should_use per {tool.__class__.__name__}: {e}")
            else:
                # Fallback to simple keyword matching
                tool_name = tool.__class__.__name__.lower()
                if tool_name in prompt_lower or self._has_tool_keywords(prompt_lower, tool_name):
                    needed_tools.append(tool)
        
        logger.info(f"🔧 Tool necessari per '{self.name}': {[t.__class__.__name__ for t in needed_tools]}")
        return needed_tools
    
    def _has_tool_keywords(self, prompt: str, tool_name: str) -> bool:
        """Check if prompt contains keywords related to the tool."""
        keyword_map = {
            "math": ["calcola", "calculate", "math", "matematica", "+", "-", "*", "/", "="],
            "search": ["cerca", "search", "google", "web", "internet"],
            "file": ["file", "documento", "leggi", "carica"],
            "code": ["codice", "programma", "script", "python"]
        }
        
        for category, keywords in keyword_map.items():
            if category in tool_name:
                return any(keyword in prompt for keyword in keywords)
        
        return False
    
    def _execute_with_tools(self, prompt: str, input_data: Dict, tools_to_use: List) -> str:
        """Execute agent with specific tools."""
        try:
            # First get LLM reasoning about the task
            reasoning_prompt = f"{prompt}\n\nAnalizza questo task e spiega come useresti i tool disponibili."
            reasoning = self.llm.generate(reasoning_prompt)
            
            # Execute tools
            tool_results = []
            for tool in tools_to_use:
                try:
                    tool_result = tool.run(input_data)
                    tool_name = tool.__class__.__name__
                    tool_results.append(f"**{tool_name}**: {tool_result}")
                    logger.info(f"✅ Tool '{tool_name}' eseguito con successo")
                except Exception as e:
                    logger.error(f"❌ Errore nell'esecuzione tool {tool.__class__.__name__}: {e}")
                    tool_results.append(f"**{tool.__class__.__name__}**: Errore - {str(e)}")
            
            # Generate final response combining reasoning and tool results
            final_prompt = f"""
Prompt originale: {input_data.get('prompt', '')}

Ragionamento iniziale: {reasoning}

Risultati dei tool:
{chr(10).join(tool_results)}

Fornisci una risposta finale completa e utile basata sui risultati dei tool:"""
            
            final_response = self.llm.generate(final_prompt)
            
            # Combine everything in a structured response
            structured_response = f"""
{final_response}

--- Dettagli Esecuzione ---
Ragionamento: {reasoning}

Tool utilizzati:
{chr(10).join(tool_results)}
"""
            
            logger.info(f"🧠 Risposta tool-based generata da '{self.name}'")
            return structured_response
            
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione con tool: {e}")
            return f"Errore nell'esecuzione con tool: {str(e)}"
    
    def _execute_without_tools(self, prompt: str) -> str:
        """Execute agent without tools."""
        try:
            response = self.llm.generate(prompt)
            logger.info(f"🧠 Risposta senza tool generata da '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"❌ Errore LLM per agente '{self.name}': {e}")
            return f"Errore LLM: {str(e)}"