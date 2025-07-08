"""
Main entry point for modular-2 framework.
Handles configuration loading, component initialization, and pipeline execution.
"""
import logging
import sys
from typing import Dict, Any
from config.yaml_parser import load_and_validate_config
from core.factory import Factory
from core.registry import registry
from managers.agent_manager import AgentManager

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('logfile.log'),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger("modular-2")

class ModularFramework:
    """
    Main framework class that orchestrates all components.
    """
    
    def __init__(self, config_path: str = "config.yaml"):
        """
        Initialize the framework.
        
        Args:
            config_path: Path to configuration file
        """
        self.config_path = config_path
        self.config = None
        self.factory = Factory()
        self.agent_manager = None
        self.registry = registry
        
        # Load configuration
        self._load_config()
        
        # Initialize components
        self._initialize_components()
    
    def _load_config(self):
        """Load and validate configuration."""
        try:
            self.config = load_and_validate_config(self.config_path)
            logger.info("✅ Configurazione caricata e validata con successo")
        except Exception as e:
            logger.error(f"❌ Errore nel caricamento configurazione: {e}")
            sys.exit(1)
    
    def _initialize_components(self):
        """Initialize all framework components."""
        try:
            # Initialize agent manager
            self.agent_manager = AgentManager(self.config, self.factory)
            logger.info("✅ Componenti inizializzati con successo")
        except Exception as e:
            logger.error(f"❌ Errore nell'inizializzazione componenti: {e}")
            sys.exit(1)
    
    def run_agent(self, agent_name: str, prompt: str) -> str:
        """
        Run a specific agent with a prompt.
        
        Args:
            agent_name: Name of the agent to run
            prompt: Input prompt
            
        Returns:
            Agent response
        """
        try:
            input_data = {"prompt": prompt}
            return self.agent_manager.run_agent(agent_name, input_data)
        except Exception as e:
            logger.error(f"❌ Errore nell'esecuzione agente '{agent_name}': {e}")
            return f"Errore: {str(e)}"
    
    def list_agents(self) -> list:
        """Get list of available agents."""
        return self.agent_manager.list_agents()
    
    def get_agent(self, agent_name: str):
        """Get agent instance by name."""
        return self.agent_manager.get_agent(agent_name)

def main():
    """Main function for testing the framework."""
    try:
        # Initialize framework
        framework = ModularFramework()
        
        # List available agents
        agents = framework.list_agents()
        print(f"🤖 Agenti disponibili: {agents}")
        
        # Test with first available agent
        if agents:
            test_agent = agents[0]
            print(f"\n🧪 Test con agente '{test_agent}':")
            
            # Test prompt
            test_prompt = "Ciao, come stai?"
            response = framework.run_agent(test_agent, test_prompt)
            print(f"👤 Prompt: {test_prompt}")
            print(f"🤖 Risposta: {response}")
        else:
            print("❌ Nessun agente disponibile")
    
    except Exception as e:
        logger.error(f"❌ Errore nel main: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()