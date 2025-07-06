from core.callbacks import BaseCallback
import logging
logger = logging.getLogger("modular-2")


class ExecutionContext:
    """
    Contesto di esecuzione per variabili, memoria, tracing, fallback.
    Tiene traccia di variabili, cronologia degli step, memoria condivisa, stato e errori.
    """
    def __init__(self):
        self.vars = {}
        self.history = []
        self.memory = {}
        self.status = {}
        self.errors = []

class Runner:
    """
    Esegue chain/agent step-by-step, gestisce input/output, fallback, tracing, variabili.
    Logga ogni step, output, errori e suggerimenti per UX avanzata.
    """
    def __init__(self, steps, callbacks=None):
        self.steps = steps
        self.callbacks = callbacks or [BaseCallback()]

    def run(self, input_data, context=None):
        """
        Esegue la pipeline step-by-step:
        - Valuta condizioni e fallback
        - Logga output e variabili
        - Gestisce errori e suggerimenti
        - Traccia la cronologia degli step
        """
        context = context or ExecutionContext()
        data = input_data
        logger.info("[INFO] Pipeline avviata.")
        try:
            for step in self.steps:
                name = step['name']
                comp = step['component']
                cond = step.get('condition')
                fallback = step.get('fallback')
                tracing = step.get('tracing', True)
                try:
                    if cond and not eval(cond, {}, context.vars):
                        logger.info(f"⏩ Step '{name}' saltato per condizione: {cond}")
                        continue
                    for cb in self.callbacks:
                        cb.on_step_start(step, data)
                    # Esecuzione step (supporta agent/tool/llm ecc.)
                    if hasattr(comp, 'run'):
                        result = comp.run(data)
                    elif callable(comp):
                        result = comp(data)
                    else:
                        raise Exception(f"Componente step '{name}' non eseguibile")
                    context.vars[step.get('output', name)] = result
                    data = result
                    for cb in self.callbacks:
                        cb.on_step_end(step, result)
                    if tracing:
                        context.history.append({'step': name, 'result': result})
                    logger.info(f"[STEP] {name} → output: {result}")
                except ModuleNotFoundError as e:
                    logger.error(f"[ERRORE] Modulo non trovato: {e}")
                    logger.error("Suggerimento: controlla che il modulo sia registrato in core/registry.py e che il nome sia corretto nel YAML.")
                    context.errors.append({'step': name, 'error': str(e)})
                    raise
                except Exception as e:
                    logger.error(f"❌ Errore step '{name}': {e}")
                    context.errors.append({'step': name, 'error': str(e)})
                    if fallback:
                        logger.info(f"↩️ Fallback step '{name}' su '{fallback}'")
                        fb_step = next((s for s in self.steps if s['name'] == fallback), None)
                        if fb_step:
                            data = self.run(data, context)
                            break
                    else:
                        logger.error("Suggerimento: usa 'python cli.py config-check --config config.yaml' per controllare la configurazione YAML.")
                        raise
            logger.info("[INFO] Pipeline completata.")
            return data
        except Exception as e:
            logger.error(f"[ERRORE] Errore durante l'esecuzione della pipeline: {e}")
            raise

# TODO: Supporto streaming, tracing avanzato, gestione errori
