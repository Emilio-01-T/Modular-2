"""
Ollama LLM Provider for modular-2 framework.
Handles communication with Ollama API.
"""
import logging
import requests
import json
from typing import Dict, Any, Optional

logger = logging.getLogger(__name__)

class OllamaLLM:
    """
    LLM provider for Ollama API.
    """
    
    def __init__(self, model: str, endpoint: str = "http://localhost:11434", **kwargs):
        """
        Initialize Ollama LLM provider.
        
        Args:
            model: Model name (e.g., 'qwen2.5-coder:latest')
            endpoint: Ollama API endpoint
            **kwargs: Additional configuration parameters
        """
        self.model = model
        self.endpoint = endpoint.rstrip('/')
        self.config = kwargs
        
        # Default parameters
        self.temperature = kwargs.get('temperature', 0.7)
        self.max_tokens = kwargs.get('max_tokens', 512)
        self.timeout = kwargs.get('timeout', 30)
        
        logger.info(f"📡 OllamaLLM inizializzato con modello: {self.model} - endpoint: {self.endpoint}")
    
    def generate(self, prompt: str, **kwargs) -> str:
        """
        Generate response from Ollama model.
        
        Args:
            prompt: Input prompt
            **kwargs: Additional generation parameters
            
        Returns:
            Generated response as string
        """
        try:
            # Prepare request data
            data = {
                "model": self.model,
                "prompt": prompt,
                "stream": False,
                "options": {
                    "temperature": kwargs.get('temperature', self.temperature),
                    "num_predict": kwargs.get('max_tokens', self.max_tokens),
                }
            }
            
            # Add any additional options from config
            for key, value in self.config.items():
                if key not in ['temperature', 'max_tokens', 'timeout']:
                    data["options"][key] = value
            
            # Make API request
            url = f"{self.endpoint}/api/generate"
            
            logger.debug(f"🔄 Invio richiesta a Ollama: {url}")
            
            response = requests.post(
                url,
                json=data,
                timeout=self.timeout,
                headers={'Content-Type': 'application/json'}
            )
            
            response.raise_for_status()
            
            # Parse response
            result = response.json()
            
            if 'response' in result:
                generated_text = result['response']
                logger.debug(f"✅ Risposta ricevuta da Ollama ({len(generated_text)} caratteri)")
                return generated_text
            else:
                logger.error(f"❌ Formato risposta Ollama non valido: {result}")
                return "Errore: formato risposta non valido"
                
        except requests.exceptions.Timeout:
            logger.error(f"❌ Timeout nella richiesta a Ollama ({self.timeout}s)")
            return "Errore: timeout nella richiesta"
        
        except requests.exceptions.ConnectionError:
            logger.error(f"❌ Impossibile connettersi a Ollama: {self.endpoint}")
            return "Errore: impossibile connettersi al server Ollama"
        
        except requests.exceptions.HTTPError as e:
            logger.error(f"❌ Errore HTTP da Ollama: {e}")
            return f"Errore HTTP: {e}"
        
        except json.JSONDecodeError:
            logger.error(f"❌ Risposta Ollama non è JSON valido")
            return "Errore: risposta non valida dal server"
        
        except Exception as e:
            logger.error(f"❌ Errore generico in OllamaLLM: {e}")
            return f"Errore: {str(e)}"
    
    def is_available(self) -> bool:
        """
        Check if Ollama service is available.
        
        Returns:
            True if service is available
        """
        try:
            url = f"{self.endpoint}/api/tags"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            
            logger.debug("✅ Ollama service disponibile")
            return True
            
        except Exception as e:
            logger.warning(f"⚠️ Ollama service non disponibile: {e}")
            return False
    
    def list_models(self) -> list:
        """
        List available models from Ollama.
        
        Returns:
            List of available model names
        """
        try:
            url = f"{self.endpoint}/api/tags"
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            models = []
            
            if 'models' in result:
                for model in result['models']:
                    if 'name' in model:
                        models.append(model['name'])
            
            logger.debug(f"📋 Modelli Ollama disponibili: {models}")
            return models
            
        except Exception as e:
            logger.error(f"❌ Errore nel recupero modelli Ollama: {e}")
            return []
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the current model.
        
        Returns:
            Model information dictionary
        """
        try:
            url = f"{self.endpoint}/api/show"
            data = {"name": self.model}
            
            response = requests.post(url, json=data, timeout=10)
            response.raise_for_status()
            
            result = response.json()
            logger.debug(f"ℹ️ Info modello {self.model} recuperate")
            return result
            
        except Exception as e:
            logger.error(f"❌ Errore nel recupero info modello: {e}")
            return {}
    
    def __str__(self) -> str:
        """String representation of the LLM provider."""
        return f"OllamaLLM(model={self.model}, endpoint={self.endpoint})"
    
    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"OllamaLLM(model='{self.model}', endpoint='{self.endpoint}', config={self.config})"