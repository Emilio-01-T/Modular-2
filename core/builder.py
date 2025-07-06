"""
builder.py - Costruzione dinamica delle pipeline e chain da configurazione YAML

- Interpreta la configurazione YAML e costruisce pipeline, chain, step dinamicamente.
- Usa registry/factory per istanziare i componenti.
- Supporta branching, condizioni, fallback, variabili.

Consulta la documentazione inline per dettagli su come estendere la logica di build.
"""

# Assembla pipeline e chain tramite LCEL

from core.lcel import LCELBuilder
from core.registry import component_registry
from core.factory import load_component_class

class PipelineBuilder:
    """Costruisce pipeline e chain da config o LCEL."""
    def __init__(self, config):
        self.config = config

    def build_chain(self, chain_cfg):
        steps = []
        for step_cfg in chain_cfg.steps:
            # Istanzia il componente corretto (llm, agent, tool, ecc.)
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
        return steps

    def build(self):
        # Costruisce tutte le chain definite in config
        chains = {}
        if hasattr(self.config, 'chains') and self.config.chains:
            for chain_cfg in self.config.chains:
                chains[chain_cfg.name] = self.build_chain(chain_cfg)
        return chains

# TODO: parsing YAML, supporto chain/agent/tool, validazione step
