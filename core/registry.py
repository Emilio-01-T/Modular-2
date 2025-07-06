import logging
from plugins.plugin_manager import discover_plugins
logger = logging.getLogger("modular-2")

# Registra e istanzia componenti dinamicamente

class ComponentRegistry:
    """
    Registry centralizzata per componenti del framework.
    Ogni tipo di modulo (llm, agent, tool, retriever, memory, loader, splitter, evaluator, parser, chain, integration)
    viene registrato qui per permettere auto-discovery, modularità e plug-and-play.
    """
    def __init__(self):
        self._registry = {  # type: dict[str, dict[str, type]]
            'llm': {},
            'agent': {},
            'tool': {},
            'retriever': {},
            'memory': {},
            'loader': {},
            'splitter': {},
            'evaluator': {},
            'parser': {},
            'chain': {},
            'integration': {},
        }

    def register(self, type_name, name, cls):
        self._registry[type_name][name] = cls
        logger.debug(f"🔗 Registrato {type_name}:{name} -> {cls}")

    def get(self, type_name, name):
        return self._registry[type_name].get(name)

    def create(self, type_name, name, *args, **kwargs):
        cls = self.get(type_name, name)
        if not cls:
            raise ValueError(f"Componente '{type_name}:{name}' non registrato.")
        return cls(*args, **kwargs)

    def register_plugin(self, plugin_class):
        """Register a plugin class under 'plugin' type."""
        self._registry.setdefault('plugin', {})[plugin_class.name] = plugin_class
        logger.debug(f"🔌 Plugin registrato: {plugin_class.name} -> {plugin_class}")

    def discover_and_register_plugins(self, plugins_dir="plugins"):
        """Auto-discover and register all plugins in the plugins/ directory."""
        plugins = discover_plugins(plugins_dir)
        for name, cls in plugins.items():
            self.register_plugin(cls)

    def list_plugins(self):
        """Return a list of registered plugin names."""
        return list(self._registry.get('plugin', {}).keys())

# Singleton globale
component_registry = ComponentRegistry()

# TODO: Registrazione automatica da config/factory, integrazione con builder LCEL
# Esempio: component_registry.register('simple_agent', SimpleAgent)

def list_registered_modules():
    """
    Restituisce un dizionario {tipo_modulo: [nomi]} per tutti i moduli registrati.
    Utile per la CLI e per la validazione/configurazione dinamica.
    """
    return {
        'llms': list(component_registry._registry.get('llm', {}).keys()),
        'tools': list(component_registry._registry.get('tool', {}).keys()),
        'retrievers': list(component_registry._registry.get('retriever', {}).keys()),
        'memory': list(component_registry._registry.get('memory', {}).keys()),
        'agents': list(component_registry._registry.get('agent', {}).keys()),
        'splitters': list(component_registry._registry.get('splitter', {}).keys()),
        'output_parsers': list(component_registry._registry.get('parser', {}).keys()),
        'evaluators': list(component_registry._registry.get('evaluator', {}).keys()),
        'integrations': list(component_registry._registry.get('integration', {}).keys()),
    }
