"""
math_tool.py - Esempio di tool matematico custom

- Implementa una funzione/tool per operazioni matematiche (addizione, sottrazione, ecc.).
- Può essere usato da agenti o pipeline tramite configurazione YAML.
- Estendibile per nuove operazioni o logica custom.

Consulta la documentazione inline per dettagli su come creare nuovi tool custom.
"""

import logging

logger = logging.getLogger(__name__)

class MathTool:
    def run(self, expression):
        logger.debug(f"🧮 MathTool ricevuto: '{expression}'")
        try:
            result = eval(expression)
            logger.debug(f"🧮 Risultato: {result}")
            return result
        except Exception as e:
            logger.error(f"❌ Errore nel calcolo '{expression}': {e}")
            return f"Errore nel calcolo: {str(e)}"
