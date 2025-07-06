"""
document_loaders.py - Loader per file, web, API, ecc.

- Permettono di caricare dati strutturati o non strutturati da varie fonti (file, web, API).
- Integrabili con retrievers, splitters e pipeline per orchestrare flussi di dati complessi.
- Possono essere estesi per supportare nuovi formati o sorgenti dati.

Consulta la documentazione inline per dettagli su come aggiungere nuovi loader o estendere la logica.
"""

import logging
logger = logging.getLogger("modular-2")

class BaseDocumentLoader:
    """Interfaccia base per document loader."""
    def load(self, source):
        raise NotImplementedError

class FileDocumentLoader(BaseDocumentLoader):
    """Loader per file locali (testo e PDF)."""
    def load(self, source):
        import os
        ext = os.path.splitext(source)[1].lower()
        logger.info(f"[Loader] Caricamento file: {source}")
        if ext == ".pdf":
            try:
                from PyPDF2 import PdfReader
                with open(source, "rb") as f:
                    reader = PdfReader(f)
                    return "\n".join(page.extract_text() or "" for page in reader.pages)
            except ImportError:
                logger.error("PyPDF2 non installato: impossibile leggere PDF.")
                return ""
        else:
            with open(source, 'r', encoding='utf-8') as f:
                return f.read()

class WebDocumentLoader(BaseDocumentLoader):
    """Loader per URL web."""
    def load(self, source):
        logger.info(f"[Loader] Caricamento URL: {source}")
        import requests
        resp = requests.get(source)
        resp.raise_for_status()
        return resp.text

class APIDocumentLoader(BaseDocumentLoader):
    """Loader per API REST (stub)."""
    def load(self, source):
        logger.info(f"[Loader] Chiamata API: {source}")
        # TODO: implementare parsing JSON/XML da API
        return f"Stub API result for: {source}"
