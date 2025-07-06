# llm/base.py
"""
base.py - Classe base per provider LLM

- Definisce l'interfaccia e i metodi comuni per tutti i provider LLM (Ollama, OpenAI, ecc.).
- Ogni nuovo provider deve estendere questa classe e implementare i metodi richiesti.
- Permette di integrare facilmente nuovi modelli LLM nel framework.

Consulta la documentazione inline per dettagli su come estendere un provider LLM custom.
"""

from abc import ABC, abstractmethod

class LLM(ABC):
    @abstractmethod
    def generate(self, prompt: str) -> str:
        pass
