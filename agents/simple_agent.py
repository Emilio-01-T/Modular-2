"""
Simple Agent implementation for modular-2 framework.
Handles basic LLM interactions with optional tools.
"""
import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

class SimpleAgent:
    """
    Simple agent that can interact with LLM and use tools.
    """
    
    def __init__(self, name: str, llm, tools: Optional[List] = None, system_prompt: str = "", config: Dict = None):
        """
        Initialize the simple agent.
        
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
        
        logger.info(f"🤖 Agente '{self.name}' inizializzato con {len(self.tools)} tool(s)")
    
    def run(self, input_data: Dict[str, Any]) -> str:
        """
        Execute the agent with given input.
        
        Args:
            input_data: Input data containing prompt and other parameters
            
        Returns:
            Agent response as string
        """
        try:
            prompt = input_data.get("prompt", "")
            
            # Prepare the full prompt with system prompt
            full_prompt = self._prepare_prompt(prompt)
            
            # Check if we need to use tools
            if self.tools and self._should_use_tools(prompt):
                return self._run_with_tools(full_prompt, input_data)
            else:
                return self._run_simple(full_prompt)
                
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione dell'agente '{self.name}': {e}")
            return f"Errore: {str(e)}"
    
    def _prepare_prompt(self, user_prompt: str) -> str:
        """Prepare the full prompt with system prompt."""
        if self.system_prompt:
            return f"{self.system_prompt}\n\nUser: {user_prompt}"
        return user_prompt
    
    def _should_use_tools(self, prompt: str) -> bool:
        """Determine if tools should be used based on the prompt."""
        # Simple heuristic - check for math operations, calculations, etc.
        tool_keywords = ["calcola", "calculate", "math", "matematica", "+", "-", "*", "/", "="]
        return any(keyword in prompt.lower() for keyword in tool_keywords)
    
    def _run_simple(self, prompt: str) -> str:
        """Run agent without tools."""
        try:
            response = self.llm.generate(prompt)
            logger.info(f"🧠 Risposta generata da '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"❌ Errore LLM per agente '{self.name}': {e}")
            return f"Errore LLM: {str(e)}"
    
    def _run_with_tools(self, prompt: str, input_data: Dict) -> str:
        """Run agent with tools available."""
        try:
            # First, get LLM response
            llm_response = self.llm.generate(prompt)
            
            # Check if we need to use any tools
            for tool in self.tools:
                if hasattr(tool, 'should_use') and tool.should_use(llm_response):
                    tool_result = tool.run(input_data)
                    llm_response += f"\n\nTool result: {tool_result}"
            
            logger.info(f"🧠 Risposta con tools generata da '{self.name}'")
            return llm_response
            
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione con tools per '{self.name}': {e}")
            return f"Errore con tools: {str(e)}"