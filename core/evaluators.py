"""
evaluators.py - Moduli per valutazione automatica output

- Valutano l'output di uno step rispetto a un riferimento (similarità, keyword, ecc.).
- Possono essere usati come step nelle chain/pipeline per autovalutazione.
- Output e metriche sono disponibili come variabili o nei log.

Consulta la documentazione inline per dettagli su come aggiungere nuovi evaluators o personalizzare la logica di valutazione.
"""

"""
Evaluators: Valutazione automatica output.
"""

import logging
logger = logging.getLogger("modular-2")

class BaseEvaluator:
    """Interfaccia base per valutatori."""
    def evaluate(self, output, reference=None):
        raise NotImplementedError

# TODO: Implementazioni per scoring, feedback, parsing YAML

class SimilarityEvaluator(BaseEvaluator):
    """Valuta la similarità tra output e reference (stub)."""
    def evaluate(self, output, reference=None):
        if not reference:
            return 0.0
        # Semplice similarità basata su parole in comune
        out_set = set(output.split())
        ref_set = set(reference.split())
        score = len(out_set & ref_set) / max(1, len(ref_set))
        logger.info(f"[Evaluator] Similarity score: {score}")
        return score

class KeywordEvaluator(BaseEvaluator):
    """Valuta la presenza di keyword nell'output."""
    def __init__(self, keywords):
        self.keywords = set(keywords)
    def evaluate(self, output, reference=None):
        found = [k for k in self.keywords if k in output]
        score = len(found) / len(self.keywords)
        logger.info(f"[Evaluator] Keyword score: {score}")
        return score
