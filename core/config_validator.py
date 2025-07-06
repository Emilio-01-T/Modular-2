import logging
import yaml
from config.schema import Config

logger = logging.getLogger("modular-2")

def validate_config(path="config.yaml") -> Config:
    logger.debug(f"📝 Validazione del file di configurazione: {path}")
    try:
        with open(path, "r") as f:
            raw = yaml.safe_load(f)
            logger.debug(f"📥 Contenuto YAML caricato: {raw}")
            config = Config(**raw)
            logger.info("✅ Configurazione validata con successo.")
            return config
    except FileNotFoundError:
        logger.critical(f"❌ File '{path}' non trovato.")
        raise
    except yaml.YAMLError as e:
        logger.error(f"❌ Errore nella sintassi YAML: {e}")
        raise
    except Exception as e:
        logger.exception(f"❌ Errore nella validazione della configurazione: {e}")
        raise
