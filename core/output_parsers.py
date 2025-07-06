"""
output_parsers.py - Moduli per parsing output strutturato (JSON, regex, ecc.)

- Estraggono dati strutturati dall'output di LLM, agent, tool, ecc.
- Possono essere usati come step nelle chain/pipeline per post-processing.
- Output strutturato disponibile come variabile per step successivi.

Consulta la documentazione inline per dettagli su come aggiungere nuovi parser o personalizzare la logica di parsing.
"""

"""
Output Parsers: Parsing output per estrazione dati strutturati.
"""

class BaseOutputParser:
    """Interfaccia base per output parser."""
    def parse(self, output):
        raise NotImplementedError

import logging
logger = logging.getLogger("modular-2")
import json
import re

class JSONOutputParser(BaseOutputParser):
    """Parser che estrae dati JSON dall'output."""
    def parse(self, output):
        try:
            return json.loads(output)
        except Exception as e:
            logger.warning(f"[OutputParser] Errore parsing JSON: {e}")
            return None

class RegexOutputParser(BaseOutputParser):
    """Parser che estrae dati tramite regex."""
    def __init__(self, pattern):
        self.pattern = re.compile(pattern)
    def parse(self, output):
        return self.pattern.findall(output)

# Pydantic parser solo come stub, richiede modello
class PydanticOutputParser(BaseOutputParser):
    """Parser che usa un modello Pydantic per validare/estrarre dati."""
    def __init__(self, model):
        self.model = model
    def parse(self, output):
        try:
            return self.model.parse_raw(output)
        except Exception as e:
            logger.warning(f"[OutputParser] Errore parsing Pydantic: {e}")
            return None
