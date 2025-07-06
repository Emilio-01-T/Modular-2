"""
LCEL (LangChain Expression Language): Linguaggio dichiarativo per costruire chain.
"""

from core.factory import load_component_class

class LCELBuilder:
    """Costruisce chain e pipeline da descrizioni dichiarative (YAML/Python)."""
    def __init__(self, config):
        self.config = config

    def build(self):
        # Interpreta chains e pipeline da config (supporta branching, fallback, condizioni)
        chains = {}
        if hasattr(self.config, 'chains') and self.config.chains:
            for chain_cfg in self.config.chains:
                steps = []
                for step_cfg in chain_cfg.steps:
                    comp = load_component_class(step_cfg.type, step_cfg.component)
                    steps.append({
                        'name': step_cfg.name,
                        'type': step_cfg.type,
                        'component': comp,
                        'input': step_cfg.input,
                        'output': step_cfg.output,
                        'condition': step_cfg.condition,
                        'fallback': step_cfg.fallback,
                        'on_error': step_cfg.on_error,
                        'tracing': step_cfg.tracing,
                        'params': step_cfg.params,
                    })
                chains[chain_cfg.name] = steps
        return chains

# TODO: Integrazione con il registry e il builder
