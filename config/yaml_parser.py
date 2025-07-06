# Gestisce la configurazione YAML e parsing

import yaml
import logging
from config.schema import Config

logger = logging.getLogger("modular-2")

def parse_yaml_config(path="config.yaml"):
    """
    Carica e restituisce la configurazione YAML come dict.
    Logga eventuali errori di parsing e fornisce feedback dettagliato.
    """
    try:
        with open(path, "r") as f:
            data = yaml.safe_load(f)
            logger.debug(f"YAML caricato: {data}")
            return data
    except Exception as e:
        logger.error(f"Errore nel parsing YAML: {e}")
        raise

def load_and_validate_config(path="config.yaml") -> Config:
    """
    Carica, valida e restituisce la configurazione come oggetto Config (pydantic).
    Se la validazione fallisce, solleva un'eccezione con messaggio dettagliato.
    """
    raw = parse_yaml_config(path)
    try:
        config = Config(**raw)
        logger.info("✅ Configurazione YAML validata e convertita in oggetto Config.")
        return config
    except Exception as e:
        logger.error(f"❌ Errore nella validazione schema Config: {e}")
        raise

def load_yaml(path="config.yaml"):
    """Carica e restituisce la configurazione YAML come dict."""
    try:
        with open(path, "r") as f:
            return yaml.safe_load(f)
    except Exception as e:
        logger.error(f"[ERRORE] Impossibile leggere il file YAML: {e}")
        return None

def validate_yaml(path="config.yaml"):
    """Valida la configurazione YAML rispetto allo schema Config. Ritorna lista errori (vuota se valida)."""
    data = load_yaml(path)
    if not data:
        return ["File YAML non trovato o non leggibile."]
    try:
        Config(**data)
        return []
    except Exception as e:
        return [str(e)]
