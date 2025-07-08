"""
Agent Manager for modular-2 framework.
Handles creation, registration and management of agents.
"""
import logging
from typing import Dict, List, Any, Optional
from core.factory import Factory

logger = logging.getLogger(__name__)

class AgentManager:
    """
    Manages the lifecycle and execution of agents.
    """
    
    def __init__(self, config: Dict, factory: Factory):
        """
        Initialize the agent manager.
        
        Args:
            config: Configuration dictionary
            factory: Factory instance for creating components
        """
        self.config = config
        self.factory = factory
        self.agents = {}
        self.tools = {}
        
        # Load tools first
        self._load_tools()
        
        # Load agents
        self._load_agents()
        
        logger.info(f"✅ Totale agenti creati: {len(self.agents)}")
    
    def _load_tools(self):
        """Load and register all tools."""
        tools_config = self.config.get("tools", [])
        
        for tool_config in tools_config:
            try:
                tool_name = tool_config.get("name")
                class_path = tool_config.get("class_path")
                tool_config_data = tool_config.get("config", {})
                
                if not tool_name or not class_path:
                    logger.warning(f"⚠️ Tool config incompleto: {tool_config}")
                    continue
                
                # Create tool instance
                tool_instance = self.factory.create_component(
                    component_type="tool",
                    class_path=class_path,
                    config=tool_config_data
                )
                
                if tool_instance:
                    self.tools[tool_name] = tool_instance
                    logger.info(f"🔧 Tool '{tool_name}' caricato con successo")
                else:
                    logger.warning(f"⚠️ Impossibile creare tool '{tool_name}'")
                    
            except Exception as e:
                logger.error(f"❌ Errore nel caricamento tool '{tool_config.get('name', 'unknown')}': {e}")
    
    def _load_agents(self):
        """Load and register all agents."""
        agents_config = self.config.get("agents", [])
        
        for agent_config in agents_config:
            try:
                agent_name = agent_config.get("name")
                agent_type = agent_config.get("type", "simple")
                
                if not agent_name:
                    logger.warning(f"⚠️ Agent config senza nome: {agent_config}")
                    continue
                
                # Create agent
                agent = self._create_agent(agent_config)
                
                if agent:
                    self.agents[agent_name] = agent
                    tool_count = len(getattr(agent, 'tools', []))
                    logger.info(f"🤖 Agente '{agent_name}' creato con {tool_count} tool(s).")
                else:
                    logger.warning(f"⚠️ Impossibile creare agente '{agent_name}'")
                    
            except Exception as e:
                logger.error(f"❌ Errore nella creazione agente '{agent_config.get('name', 'unknown')}': {e}")
    
    def _create_agent(self, agent_config: Dict) -> Optional[Any]:
        """Create a single agent based on configuration."""
        agent_name = agent_config.get("name")
        agent_type = agent_config.get("type", "simple")
        llm_name = agent_config.get("llm")
        tool_names = agent_config.get("tools", [])
        system_prompt = agent_config.get("system_prompt", "")
        config = agent_config.get("config", {})
        
        try:
            # Get LLM instance
            llm = self._get_llm_instance(llm_name)
            if not llm:
                logger.error(f"❌ LLM '{llm_name}' non trovato per agente '{agent_name}'")
                return None
            
            # Get tool instances
            agent_tools = []
            for tool_name in tool_names:
                if tool_name in self.tools:
                    agent_tools.append(self.tools[tool_name])
                    logger.debug(f"🔧 Tool '{tool_name}' aggiunto all'agente '{agent_name}'")
                else:
                    logger.warning(f"⚠️ Tool '{tool_name}' non trovato per agente '{agent_name}'")
            
            # Create agent based on type
            if agent_type == "simple":
                from agents.simple_agent import SimpleAgent
                return SimpleAgent(
                    name=agent_name,
                    llm=llm,
                    tools=agent_tools,
                    system_prompt=system_prompt,
                    config=config
                )
            
            elif agent_type == "multi_tool":
                from agents.multi_tool_agent import MultiToolAgent
                dispatch_strategy = agent_config.get("dispatch_strategy", "keyword")
                return MultiToolAgent(
                    name=agent_name,
                    llm=llm,
                    tools=agent_tools,
                    system_prompt=system_prompt,
                    dispatch_strategy=dispatch_strategy,
                    config=config
                )
            
            elif agent_type == "agentic_automation":
                from agents.agentic_automation_agent import AgenticAutomationAgent
                max_iterations = agent_config.get("max_iterations", 5)
                return AgenticAutomationAgent(
                    name=agent_name,
                    llm=llm,
                    tools=agent_tools,
                    system_prompt=system_prompt,
                    max_iterations=max_iterations,
                    config=config
                )
            
            elif agent_type == "tool":
                from agents.tool_agent import ToolAgent
                return ToolAgent(
                    name=agent_name,
                    llm=llm,
                    tools=agent_tools,
                    system_prompt=system_prompt,
                    config=config
                )
            
            else:
                logger.error(f"❌ Tipo agente sconosciuto: '{agent_type}' per agente '{agent_name}'")
                return None
                
        except Exception as e:
            logger.error(f"❌ Errore nella creazione agente '{agent_name}': {e}")
            return None
    
    def _get_llm_instance(self, llm_name: str) -> Optional[Any]:
        """Get LLM instance by name."""
        try:
            # Try to get from factory registry
            llm_config = self._find_llm_config(llm_name)
            if not llm_config:
                logger.error(f"❌ Configurazione LLM '{llm_name}' non trovata")
                return None
            
            provider = llm_config.get("provider")
            model = llm_config.get("model")
            endpoint = llm_config.get("endpoint")
            api_key = llm_config.get("api_key")
            config = llm_config.get("config", {})
            
            if provider == "ollama":
                from llm_providers.ollama_llm import OllamaLLM
                return OllamaLLM(
                    model=model,
                    endpoint=endpoint,
                    **config
                )
            elif provider == "openai":
                from llm_providers.openai_llm import OpenAILLM
                return OpenAILLM(
                    model=model,
                    api_key=api_key,
                    **config
                )
            else:
                logger.error(f"❌ Provider LLM sconosciuto: '{provider}'")
                return None
                
        except Exception as e:
            logger.error(f"❌ Errore nella creazione LLM '{llm_name}': {e}")
            return None
    
    def _find_llm_config(self, llm_name: str) -> Optional[Dict]:
        """Find LLM configuration by name."""
        # Check single LLM config
        llm_config = self.config.get("llm")
        if llm_config and llm_config.get("provider") == llm_name:
            return llm_config
        
        # Check multiple LLMs config
        llms_config = self.config.get("llms", [])
        for llm in llms_config:
            if llm.get("name") == llm_name:
                return llm
        
        # Fallback to single LLM config if name matches provider
        if llm_config:
            return llm_config
        
        return None
    
    def get_agent(self, agent_name: str) -> Optional[Any]:
        """Get agent by name."""
        return self.agents.get(agent_name)
    
    def list_agents(self) -> List[str]:
        """Get list of all agent names."""
        return list(self.agents.keys())
    
    def run_agent(self, agent_name: str, input_data: Dict[str, Any]) -> str:
        """Run a specific agent with given input."""
        agent = self.get_agent(agent_name)
        if not agent:
            return f"Agente '{agent_name}' non trovato"
        
        try:
            return agent.run(input_data)
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione agente '{agent_name}': {e}")
            return f"Errore nell'esecuzione: {str(e)}"