"""
ollama_llm.py - Provider LLM per Ollama

- Implementa la classe LLM specifica per Ollama, estendendo la base LLM.
- Gestisce la configurazione (endpoint, modello, parametri custom).
- Può essere usato da agenti, chain, pipeline tramite configurazione YAML.

Consulta la documentazione inline per dettagli su come configurare e usare Ollama LLM.
"""

import requests
import logging

logger = logging.getLogger(__name__)

class OllamaLLM:
    def __init__(self, model, endpoint, api_key=None):
        self.model = model
        self.endpoint = endpoint.rstrip("/")
        self.api_key = api_key
        logger.info(f"📡 OllamaLLM inizializzato con modello: {model} - endpoint: {self.endpoint}")

    def generate(self, prompt: str) -> str:
        url = f"{self.endpoint}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": False
        }
        headers = {"Content-Type": "application/json"}

        logger.debug(f"🔁 Invio prompt a Ollama: {prompt[:60]}...")
        try:
            response = requests.post(url, json=payload, headers=headers)
            response.raise_for_status()
            data = response.json()
            logger.debug(f"[OLLAMA DEBUG] Risposta JSON: {data}")
            logger.debug("✅ Risposta ricevuta correttamente da Ollama.")
            return data["response"]
        except Exception as e:
            logger.error(f"❌ Errore nella richiesta a Ollama: {e}")
            raise

    def stream_generate(self, prompt: str):
        """
        Genera risposta in streaming (chunk-by-chunk) dalla API Ollama.
        Ritorna un generatore che produce i chunk di testo.
        """
        import requests
        url = f"{self.endpoint}/api/generate"
        payload = {
            "model": self.model,
            "prompt": prompt,
            "stream": True
        }
        headers = {"Content-Type": "application/json"}
        logger.debug(f"🔁 [STREAM] Invio prompt a Ollama: {prompt[:60]}...")
        try:
            with requests.post(url, json=payload, headers=headers, stream=True) as resp:
                resp.raise_for_status()
                for line in resp.iter_lines():
                    if line:
                        try:
                            import json
                            data = json.loads(line)
                            chunk = data.get("response", "")
                            if chunk:
                                yield chunk
                        except Exception as e:
                            logger.warning(f"[STREAM] Errore parsing chunk: {e}")
        except Exception as e:
            logger.error(f"❌ Errore nella richiesta streaming a Ollama: {e}")
            raise
