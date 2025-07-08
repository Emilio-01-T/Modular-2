"""
Registry module for modular-2 framework.
Centralized registry for all component types.
"""
import logging
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class Registry:
    """
    Central registry for all framework components.
    """
    
    def __init__(self):
        """Initialize the registry."""
        self.components = {
            "llm": {},
            "agent": {},
            "tool": {},
            "memory": {},
            "retriever": {},
            "loader": {},
            "splitter": {},
            "evaluator": {},
            "parser": {},
            "integration": {},
            "plugin": {}
        }
        self._register_default_components()
        logger.debug("📋 Registry inizializzato")
    
    def _register_default_components(self):
        """Register default framework components."""
        # LLM Providers
        self.register("llm", "ollama", "llm_providers.ollama_llm.OllamaLLM")
        self.register("llm", "openai", "llm_providers.openai_llm.OpenAILLM")
        
        # Agents
        self.register("agent", "simple", "agents.simple_agent.SimpleAgent")
        self.register("agent", "multi_tool", "agents.multi_tool_agent.MultiToolAgent")
        self.register("agent", "agentic_automation", "agents.agentic_automation_agent.AgenticAutomationAgent")
        self.register("agent", "tool", "agents.tool_agent.ToolAgent")
        
        # Tools
        self.register("tool", "math", "tools.math_tool.MathTool")
        
        # Memory
        self.register("memory", "conversation", "core.memory.ConversationMemory")
        self.register("memory", "buffer", "core.memory.BufferMemory")
        
        # Retrievers
        self.register("retriever", "semantic", "core.retrievers.SemanticRetriever")
        self.register("retriever", "chroma", "core.retrievers.ChromaDBRetriever")
        
        # Document Loaders
        self.register("loader", "file", "core.document_loaders.FileDocumentLoader")
        self.register("loader", "web", "core.document_loaders.WebDocumentLoader")
        
        # Text Splitters
        self.register("splitter", "word", "core.text_splitters.WordChunkSplitter")
        self.register("splitter", "line", "core.text_splitters.LineSplitter")
        
        # Evaluators
        self.register("evaluator", "simple", "core.evaluators.SimpleEvaluator")
        
        # Output Parsers
        self.register("parser", "json", "core.output_parsers.JSONOutputParser")
        self.register("parser", "regex", "core.output_parsers.RegexOutputParser")
        
        # Integrations
        self.register("integration", "pandas", "plugins.pandas_integration.PandasIntegration")
        self.register("integration", "slack", "plugins.slack_integration.SlackIntegration")
        self.register("integration", "sql", "plugins.sql_integration.SQLIntegration")
        
        # Plugins
        self.register("plugin", "automation", "plugins.automation_plugin.AutomationPlugin")
        self.register("plugin", "web_search", "plugins.web_search_plugin.WebSearchPlugin")
        self.register("plugin", "searxng", "plugins.searxng_plugin.SearXNGPlugin")
        
        logger.info("✅ Componenti default registrati nel registry")
    
    def register(self, component_type: str, name: str, class_path: str):
        """
        Register a component in the registry.
        
        Args:
            component_type: Type of component (llm, agent, tool, etc.)
            name: Component name
            class_path: Full class path
        """
        if component_type not in self.components:
            self.components[component_type] = {}
        
        self.components[component_type][name] = class_path
        logger.debug(f"📝 Registrato {component_type}.{name} -> {class_path}")
    
    def get(self, component_type: str, name: str) -> Optional[str]:
        """
        Get component class path by type and name.
        
        Args:
            component_type: Type of component
            name: Component name
            
        Returns:
            Class path or None if not found
        """
        return self.components.get(component_type, {}).get(name)
    
    def list_components(self, component_type: str = None) -> Dict[str, Any]:
        """
        List all registered components.
        
        Args:
            component_type: Optional filter by component type
            
        Returns:
            Dictionary of components
        """
        if component_type:
            return self.components.get(component_type, {})
        return self.components
    
    def list_registered_modules(self) -> Dict[str, List[str]]:
        """
        List all registered modules by type.
        
        Returns:
            Dictionary with component types as keys and lists of names as values
        """
        result = {}
        for comp_type, components in self.components.items():
            result[comp_type] = list(components.keys())
        return result
    
    def is_registered(self, component_type: str, name: str) -> bool:
        """
        Check if a component is registered.
        
        Args:
            component_type: Type of component
            name: Component name
            
        Returns:
            True if registered
        """
        return name in self.components.get(component_type, {})
    
    def unregister(self, component_type: str, name: str) -> bool:
        """
        Unregister a component.
        
        Args:
            component_type: Type of component
            name: Component name
            
        Returns:
            True if successfully unregistered
        """
        if component_type in self.components and name in self.components[component_type]:
            del self.components[component_type][name]
            logger.debug(f"🗑️ Rimosso {component_type}.{name} dal registry")
            return True
        return False
    
    def clear(self, component_type: str = None):
        """
        Clear registry.
        
        Args:
            component_type: Optional specific type to clear
        """
        if component_type:
            self.components[component_type] = {}
            logger.debug(f"🧹 Registry {component_type} pulito")
        else:
            for comp_type in self.components:
                self.components[comp_type] = {}
            logger.debug("🧹 Registry completamente pulito")

# Global registry instance
registry = Registry()