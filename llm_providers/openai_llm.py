"""
openai_llm.py - Provider LLM per OpenAI

- Implementa la classe LLM specifica per OpenAI, estendendo la base LLM.
- Gestisce la configurazione (endpoint, modello, api_key).
- Può essere usato da agenti, chain, pipeline tramite configurazione YAML.

"""

import requests
import logging
from .base import LLM

logger = logging.getLogger(__name__)

class OpenAILLM(LLM):
    def __init__(self, model, api_key, endpoint=None):
        self.model = model
        self.api_key = api_key
        self.endpoint = endpoint or "https://api.openai.com/v1/chat/completions"
        logger.info(f"🌐 OpenAILLM inizializzato con modello: {model} - endpoint: {self.endpoint}")

    def generate(self, prompt: str) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": self.model,
            "messages": [
                {"role": "user", "content": prompt}
            ]
        }
        logger.debug(f"🔁 Invio prompt a OpenAI: {prompt[:60]}...")
        try:
            response = requests.post(self.endpoint, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"[OPENAI DEBUG] Risposta JSON: {data}")
            logger.debug("✅ Risposta ricevuta correttamente da OpenAI.")
            return data["choices"][0]["message"]["content"]
        except Exception as e:
            logger.error(f"❌ Errore nella richiesta a OpenAI: {e}")
            raise
