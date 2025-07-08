"""
Multi-Tool Agent implementation for modular-2 framework.
Advanced agent that can intelligently select and use multiple tools.
"""
import logging
from typing import List, Dict, Any, Optional
import re

logger = logging.getLogger(__name__)

class MultiToolAgent:
    """
    Advanced agent that can intelligently select and use multiple tools.
    """
    
    def __init__(self, name: str, llm, tools: Optional[List] = None, 
                 system_prompt: str = "", dispatch_strategy: str = "keyword", config: Dict = None):
        """
        Initialize the multi-tool agent.
        
        Args:
            name: Agent name
            llm: LLM provider instance
            tools: List of tool instances
            system_prompt: System prompt for the agent
            dispatch_strategy: Strategy for tool selection ('keyword', 'llm', 'sequential')
            config: Additional configuration
        """
        self.name = name
        self.llm = llm
        self.tools = tools or []
        self.system_prompt = system_prompt
        self.dispatch_strategy = dispatch_strategy
        self.config = config or {}
        
        # Create tool mapping for easy access
        self.tool_map = {tool.__class__.__name__.lower(): tool for tool in self.tools}
        
        logger.info(f"🔧 Multi-tool agente '{self.name}' inizializzato con {len(self.tools)} tool(s)")
        logger.info(f"📋 Tools disponibili: {list(self.tool_map.keys())}")
    
    def run(self, input_data: Dict[str, Any]) -> str:
        """
        Execute the agent with intelligent tool selection.
        
        Args:
            input_data: Input data containing prompt and other parameters
            
        Returns:
            Agent response as string
        """
        try:
            prompt = input_data.get("prompt", "")
            
            # Prepare the full prompt
            full_prompt = self._prepare_prompt(prompt)
            
            # Select appropriate tools based on strategy
            selected_tools = self._select_tools(prompt)
            
            if selected_tools:
                return self._run_with_selected_tools(full_prompt, input_data, selected_tools)
            else:
                return self._run_simple(full_prompt)
                
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione del multi-tool agente '{self.name}': {e}")
            return f"Errore: {str(e)}"
    
    def _prepare_prompt(self, user_prompt: str) -> str:
        """Prepare the full prompt with system prompt and tool information."""
        tool_info = ""
        if self.tools:
            tool_names = [tool.__class__.__name__ for tool in self.tools]
            tool_info = f"\n\nTools disponibili: {', '.join(tool_names)}"
        
        if self.system_prompt:
            return f"{self.system_prompt}{tool_info}\n\nUser: {user_prompt}"
        return f"{tool_info}\n\nUser: {user_prompt}"
    
    def _select_tools(self, prompt: str) -> List:
        """Select appropriate tools based on the dispatch strategy."""
        if self.dispatch_strategy == "keyword":
            return self._select_tools_by_keyword(prompt)
        elif self.dispatch_strategy == "llm":
            return self._select_tools_by_llm(prompt)
        elif self.dispatch_strategy == "sequential":
            return self.tools  # Use all tools in sequence
        else:
            return []
    
    def _select_tools_by_keyword(self, prompt: str) -> List:
        """Select tools based on keyword matching."""
        selected = []
        prompt_lower = prompt.lower()
        
        # Define keyword mappings for different tools
        tool_keywords = {
            "math": ["calcola", "calculate", "math", "matematica", "+", "-", "*", "/", "=", "numero", "number"],
            "search": ["cerca", "search", "google", "web", "internet", "trova", "find"],
            "file": ["file", "documento", "document", "leggi", "read", "carica", "load"],
            "code": ["codice", "code", "programma", "program", "script", "python", "javascript"]
        }
        
        for tool in self.tools:
            tool_name = tool.__class__.__name__.lower()
            
            # Check direct tool name match
            if tool_name in prompt_lower:
                selected.append(tool)
                continue
            
            # Check keyword matches
            for category, keywords in tool_keywords.items():
                if category in tool_name:
                    if any(keyword in prompt_lower for keyword in keywords):
                        selected.append(tool)
                        break
        
        logger.info(f"🎯 Tools selezionati per '{self.name}': {[t.__class__.__name__ for t in selected]}")
        return selected
    
    def _select_tools_by_llm(self, prompt: str) -> List:
        """Use LLM to select appropriate tools."""
        if not self.tools:
            return []
        
        tool_descriptions = []
        for i, tool in enumerate(self.tools):
            tool_name = tool.__class__.__name__
            tool_desc = getattr(tool, 'description', f"Tool for {tool_name}")
            tool_descriptions.append(f"{i}: {tool_name} - {tool_desc}")
        
        selection_prompt = f"""
Dato il seguente prompt dell'utente, seleziona i tool più appropriati da usare.
Rispondi solo con i numeri dei tool separati da virgola (es: 0,2).

Prompt utente: {prompt}

Tool disponibili:
{chr(10).join(tool_descriptions)}

Tool selezionati:"""
        
        try:
            response = self.llm.generate(selection_prompt)
            # Parse the response to get tool indices
            indices = re.findall(r'\d+', response)
            selected = []
            for idx in indices:
                try:
                    tool_idx = int(idx)
                    if 0 <= tool_idx < len(self.tools):
                        selected.append(self.tools[tool_idx])
                except ValueError:
                    continue
            
            logger.info(f"🤖 LLM ha selezionato tools per '{self.name}': {[t.__class__.__name__ for t in selected]}")
            return selected
            
        except Exception as e:
            logger.warning(f"⚠️ Errore nella selezione LLM, fallback a keyword: {e}")
            return self._select_tools_by_keyword(prompt)
    
    def _run_simple(self, prompt: str) -> str:
        """Run agent without tools."""
        try:
            response = self.llm.generate(prompt)
            logger.info(f"🧠 Risposta semplice generata da '{self.name}'")
            return response
        except Exception as e:
            logger.error(f"❌ Errore LLM per agente '{self.name}': {e}")
            return f"Errore LLM: {str(e)}"
    
    def _run_with_selected_tools(self, prompt: str, input_data: Dict, selected_tools: List) -> str:
        """Run agent with selected tools."""
        try:
            # Get initial LLM response
            llm_response = self.llm.generate(prompt)
            
            # Execute selected tools
            tool_results = []
            for tool in selected_tools:
                try:
                    tool_result = tool.run(input_data)
                    tool_name = tool.__class__.__name__
                    tool_results.append(f"{tool_name}: {tool_result}")
                    logger.info(f"🔧 Tool '{tool_name}' eseguito con successo")
                except Exception as e:
                    logger.warning(f"⚠️ Errore nell'esecuzione del tool {tool.__class__.__name__}: {e}")
                    tool_results.append(f"{tool.__class__.__name__}: Errore - {str(e)}")
            
            # Combine LLM response with tool results
            if tool_results:
                final_response = f"{llm_response}\n\n--- Tool Results ---\n" + "\n".join(tool_results)
            else:
                final_response = llm_response
            
            logger.info(f"🧠 Risposta multi-tool generata da '{self.name}'")
            return final_response
            
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione multi-tool per '{self.name}': {e}")
            return f"Errore multi-tool: {str(e)}"