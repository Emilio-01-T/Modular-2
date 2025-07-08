"""
YAML Parser for modular-2 framework configuration.
Handles loading and validation of YAML configuration files.
"""
import yaml
import logging
from typing import Dict, Any
from pathlib import Path

logger = logging.getLogger(__name__)

def load_yaml_file(file_path: str) -> Dict[str, Any]:
    """
    Load YAML file and return parsed content.
    
    Args:
        file_path: Path to YAML file
        
    Returns:
        Parsed YAML content as dictionary
        
    Raises:
        FileNotFoundError: If file doesn't exist
        yaml.YAMLError: If YAML parsing fails
    """
    try:
        path = Path(file_path)
        
        if not path.exists():
            raise FileNotFoundError(f"File di configurazione non trovato: {file_path}")
        
        with open(path, 'r', encoding='utf-8') as file:
            content = yaml.safe_load(file)
            
        if content is None:
            logger.warning(f"⚠️ File YAML vuoto: {file_path}")
            return {}
        
        logger.debug(f"📄 File YAML caricato: {file_path}")
        return content
        
    except yaml.YAMLError as e:
        logger.error(f"❌ Errore nel parsing YAML: {e}")
        raise
    except Exception as e:
        logger.error(f"❌ Errore nel caricamento file: {e}")
        raise

def validate_config_structure(config: Dict[str, Any]) -> bool:
    """
    Validate basic configuration structure.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        True if valid structure
        
    Raises:
        ValueError: If structure is invalid
    """
    try:
        # Check for required sections
        required_sections = []  # No strictly required sections for flexibility
        
        for section in required_sections:
            if section not in config:
                raise ValueError(f"Sezione richiesta mancante: {section}")
        
        # Validate LLM configuration
        if 'llm' in config:
            llm_config = config['llm']
            if not isinstance(llm_config, dict):
                raise ValueError("Sezione 'llm' deve essere un dizionario")
            
            if 'provider' not in llm_config:
                raise ValueError("Campo 'provider' richiesto nella sezione 'llm'")
        
        # Validate agents configuration
        if 'agents' in config:
            agents_config = config['agents']
            if not isinstance(agents_config, list):
                raise ValueError("Sezione 'agents' deve essere una lista")
            
            for i, agent in enumerate(agents_config):
                if not isinstance(agent, dict):
                    raise ValueError(f"Agente {i} deve essere un dizionario")
                
                if 'name' not in agent:
                    raise ValueError(f"Campo 'name' richiesto per agente {i}")
        
        # Validate tools configuration
        if 'tools' in config:
            tools_config = config['tools']
            if not isinstance(tools_config, list):
                raise ValueError("Sezione 'tools' deve essere una lista")
            
            for i, tool in enumerate(tools_config):
                if not isinstance(tool, dict):
                    raise ValueError(f"Tool {i} deve essere un dizionario")
                
                if 'name' not in tool:
                    raise ValueError(f"Campo 'name' richiesto per tool {i}")
                
                if 'class_path' not in tool:
                    raise ValueError(f"Campo 'class_path' richiesto per tool {i}")
        
        logger.debug("✅ Struttura configurazione validata")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore nella validazione struttura: {e}")
        raise

def load_and_validate_config(file_path: str) -> Dict[str, Any]:
    """
    Load and validate configuration file.
    
    Args:
        file_path: Path to configuration file
        
    Returns:
        Validated configuration dictionary
        
    Raises:
        Various exceptions for different validation errors
    """
    try:
        # Load YAML file
        config = load_yaml_file(file_path)
        
        # Validate structure
        validate_config_structure(config)
        
        logger.info("✅ Configurazione YAML validata e convertita in oggetto Config.")
        return config
        
    except Exception as e:
        logger.error(f"❌ Errore nel caricamento/validazione configurazione: {e}")
        raise

def save_config_to_yaml(config: Dict[str, Any], file_path: str) -> bool:
    """
    Save configuration dictionary to YAML file.
    
    Args:
        config: Configuration dictionary
        file_path: Output file path
        
    Returns:
        True if successful
    """
    try:
        path = Path(file_path)
        
        with open(path, 'w', encoding='utf-8') as file:
            yaml.dump(config, file, default_flow_style=False, allow_unicode=True, indent=2)
        
        logger.info(f"✅ Configurazione salvata in: {file_path}")
        return True
        
    except Exception as e:
        logger.error(f"❌ Errore nel salvataggio configurazione: {e}")
        return False