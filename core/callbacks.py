"""
callbacks.py - Gestione dei callback per tracing, logging, errori, fallback, condizioni.

- Definisce la classe base per i callback (BaseCallback).
- Permette di tracciare l'esecuzione step-by-step, loggare errori, fallback, condizioni.
- Puoi estendere BaseCallback per implementare tracing custom, logging avanzato, metriche, ecc.

Consulta la documentazione inline per esempi di callback custom.
"""

import logging

logger = logging.getLogger("modular-2")

class BaseCallback:
    """
    Classe base per la gestione dei callback.

    Questa classe definisce i metodi che possono essere sovrascritti per gestire
    eventi specifici durante l'esecuzione di un processo modulare. I metodi includono
    on_step_start, on_step_end, on_agent_start, on_agent_end, on_fallback, on_condition, e on_error.

    Ogni metodo riceve argomenti pertinenti all'evento, come 'step', 'agent', 'data', 'result', 'error', ecc.
    """

    def on_step_start(self, step, data):
        """
        Chiamato all'inizio di ogni step.

        :param step: L'oggetto step corrente.
        :param data: I dati in ingresso per lo step.
        """
        logger.debug(f"[CALLBACK] Step start: {getattr(step, 'name', str(step))} | Input: {data}")

    def on_step_end(self, step, data):
        """
        Chiamato alla fine di ogni step.

        :param step: L'oggetto step corrente.
        :param data: I dati in uscita dallo step.
        """
        logger.debug(f"[CALLBACK] Step end: {getattr(step, 'name', str(step))} | Output: {data}")

    def on_agent_start(self, agent, data):
        """
        Chiamato all'inizio dell'esecuzione di un agente.

        :param agent: L'oggetto agente corrente.
        :param data: I dati in ingresso per l'agente.
        """
        logger.debug(f"[CALLBACK] Agent start: {getattr(agent, 'name', str(agent))} | Input: {data}")

    def on_agent_end(self, agent, result):
        """
        Chiamato alla fine dell'esecuzione di un agente.

        :param agent: L'oggetto agente corrente.
        :param result: Il risultato prodotto dall'agente.
        """
        logger.debug(f"[CALLBACK] Agent end: {getattr(agent, 'name', str(agent))} | Output: {result}")

    def on_fallback(self, step, error):
        """
        Chiamato quando viene attivato un fallback.

        :param step: L'oggetto step corrente.
        :param error: L'errore che ha causato l'attivazione del fallback.
        """
        logger.warning(f"[CALLBACK] Fallback triggered for step: {getattr(step, 'name', str(step))} | Error: {error}")

    def on_condition(self, step, condition, result):
        """
        Chiamato quando viene valutata una condizione.

        :param step: L'oggetto step corrente.
        :param condition: La condizione valutata.
        :param result: Il risultato della valutazione della condizione.
        """
        logger.info(f"[CALLBACK] Condition evaluated for step: {getattr(step, 'name', str(step))} | Condition: {condition} | Result: {result}")

    def on_error(self, step, error):
        """
        Chiamato in caso di errore durante l'esecuzione di uno step.

        :param step: L'oggetto step corrente.
        :param error: L'errore verificatosi.
        """
        logger.error(f"[CALLBACK] Error in step: {getattr(step, 'name', str(step))} | Error: {error}")
