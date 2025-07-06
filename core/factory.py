"""
factory.py - Factory per l'istanziazione dinamica dei componenti

- Permette di creare istanze di moduli (LLM, agent, tool, ecc.) a partire da stringhe/class_path.
- Si integra con il registry per la risoluzione dei nomi.
- Utile per estendere il framework con nuovi moduli plug-and-play.

Consulta la documentazione inline per dettagli su come aggiungere nuovi componenti.
"""

import importlib
import logging

from core.registry import component_registry

logger = logging.getLogger("modular-2")

def load_class_from_key(class_map, key):
    if key not in class_map:
        logger.error(f"🔑 Chiave '{key}' non trovata nella mappa delle classi.")
        raise ValueError(f"Chiave '{key}' non valida.")
    
    module_name, class_name = class_map[key].rsplit('.', 1)
    logger.debug(f"📦 Importazione modulo '{module_name}', classe '{class_name}'")
    
    try:
        module = importlib.import_module(module_name)
        cls = getattr(module, class_name)
        logger.debug(f"✅ Classe '{class_name}' caricata con successo.")
        return cls
    except Exception as e:
        logger.exception(f"❌ Errore durante il caricamento della classe '{class_name}' da '{module_name}': {e}")
        raise

LLM_CLASSES = {
    "openai": "llm_providers.openai_llm.OpenAILLM",
    "ollama": "llm_providers.ollama_llm.OllamaLLM"
}
AGENT_CLASSES = {
    "simple": "agents.simple_agent.SimpleAgent",
    "math": "tools.math_tool.MathTool"
}
TOOL_CLASSES = {
    "math": "tools.math_tool.MathTool",
    "calculator": "tools.calculator_tool.CalculatorTool"
}

# Registry di mapping per ogni tipo di componente
CHAIN_CLASSES = {}
RETRIEVER_CLASSES = {}
MEMORY_CLASSES = {}
LOADER_CLASSES = {}
SPLITTER_CLASSES = {}
EVALUATOR_CLASSES = {}
PARSER_CLASSES = {}
INTEGRATION_CLASSES = {}

# Funzione generica per caricare una classe da registry dinamico
def load_component_class(type_name, key):
    """Carica una classe dal registry dinamico o dai mapping statici."""
    # Prima cerca nel registry dinamico
    cls = component_registry.get(type_name, key)
    if cls:
        logger.debug(f"[Factory] Classe trovata nel registry: {type_name}.{key}")
        return cls
    # Fallback su mapping statici
    static_maps = {
        'llm': LLM_CLASSES,
        'agent': AGENT_CLASSES,
        'tool': TOOL_CLASSES,
        'chain': CHAIN_CLASSES,
        'retriever': RETRIEVER_CLASSES,
        'memory': MEMORY_CLASSES,
        'loader': LOADER_CLASSES,
        'splitter': SPLITTER_CLASSES,
        'evaluator': EVALUATOR_CLASSES,
        'parser': PARSER_CLASSES,
        'integration': INTEGRATION_CLASSES,
    }
    class_map = static_maps.get(type_name)
    if class_map and key in class_map:
        return load_class_from_key(class_map, key)
    logger.error(f"[Factory] Nessuna classe trovata per {type_name}.{key}")
    raise ValueError(f"Classe non trovata per {type_name}.{key}")