"""
chains.py - Definizione e gestione di chain (sequenze di step modulari)

- Orchestrano l'esecuzione di step (llm, agent, tool, memory, retriever, ecc.) in sequenza o con branching/fallback.
- Supportano condizioni, variabili, fallback, tracing.
- Permettono di comporre pipeline complesse e riusabili.

Consulta la documentazione inline per dettagli su come estendere o personalizzare le chain.
"""

"""
Chains (Catene): Sequenze modulari di chiamate LLM e funzioni.
Definisce la logica step-by-step delle pipeline.
"""

from core.runner import ExecutionContext
from core.callbacks import BaseCallback
import logging
logger = logging.getLogger("modular-2")

class BaseChain:
    """Interfaccia base per una chain."""
    def __init__(self, steps=None):
        self.steps = steps or []

    def run(self, input_data):
        data = input_data
        for step in self.steps:
            data = step.run(data)
        return data

class DynamicChain(BaseChain):
    """Chain generica che esegue step dinamici con fallback, condizioni, tracing."""
    def __init__(self, steps, callbacks=None):
        super().__init__(steps)
        self.callbacks = callbacks or [BaseCallback()]

    def run(self, input_data, context=None):
        context = context or ExecutionContext()
        data = input_data
        for step in self.steps:
            # Supporta step come dict (come da builder)
            if isinstance(step, dict):
                name = step.get('name', str(step))
                cond = step.get('condition')
                fallback = step.get('fallback')
                tracing = step.get('tracing', True)
                comp = step.get('component')
                try:
                    for cb in self.callbacks:
                        cb.on_step_start(step, data)
                    if cond:
                        cond_result = eval(cond, {}, context.vars)
                        for cb in self.callbacks:
                            cb.on_condition(step, cond, cond_result)
                        if not cond_result:
                            continue
                    if hasattr(comp, 'run'):
                        result = comp.run(data)
                    elif callable(comp):
                        result = comp(data)
                    else:
                        raise Exception(f"Step '{name}' non eseguibile")
                    context.vars[name] = result
                    data = result
                    for cb in self.callbacks:
                        cb.on_step_end(step, result)
                except Exception as e:
                    logger.error(f"❌ Errore step '{name}': {e}")
                    for cb in self.callbacks:
                        cb.on_error(step, e)
                    if fallback:
                        for cb in self.callbacks:
                            cb.on_fallback(step, e)
                        # Cerca step fallback e riesegui
                        fb_step = next((s for s in self.steps if (isinstance(s, dict) and s.get('name') == fallback)), None)
                        if fb_step:
                            data = self.__class__([fb_step], self.callbacks).run(data, context)
                            continue
                    else:
                        raise
            else:
                # Vecchio stile: step come oggetto
                name = getattr(step, 'name', str(step))
                try:
                    for cb in self.callbacks:
                        cb.on_step_start(step, data)
                    if hasattr(step, 'condition') and step.condition:
                        cond_result = eval(step.condition, {}, context.vars)
                        for cb in self.callbacks:
                            cb.on_condition(step, step.condition, cond_result)
                        if not cond_result:
                            continue
                    if hasattr(step, 'run'):
                        result = step.run(data)
                    elif callable(step):
                        result = step(data)
                    else:
                        raise Exception(f"Step '{name}' non eseguibile")
                    context.vars[name] = result
                    data = result
                    for cb in self.callbacks:
                        cb.on_step_end(step, result)
                except Exception as e:
                    logger.error(f"❌ Errore step '{name}': {e}")
                    for cb in self.callbacks:
                        cb.on_error(step, e)
                    if hasattr(step, 'fallback') and step.fallback:
                        for cb in self.callbacks:
                            cb.on_fallback(step, e)
                        fb_step = next((s for s in self.steps if getattr(s, 'name', str(s)) == step.fallback), None)
                        if fb_step:
                            data = self.__class__([fb_step], self.callbacks).run(data, context)
                            continue
                    else:
                        raise
        return data

# TODO: Implementazioni concrete di chain, parsing da YAML, integrazione LCEL
