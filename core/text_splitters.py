"""
text_splitters.py - Moduli per chunking/suddivisione testi

- Suddividono testi/documenti in chunk per il retrieval, l'indicizzazione o il processing LLM.
- Possono essere usati da retrievers, loader, pipeline o agenti.
- Permettono di ottimizzare la granularità dei dati processati.

Consulta la documentazione inline per dettagli su come aggiungere nuovi splitter o personalizzare la logica di chunking.
"""

"""
Text Splitters: Divisione documenti in chunk.
"""

class BaseTextSplitter:
    """Interfaccia base per text splitter."""
    def split(self, text):
        raise NotImplementedError

# TODO: Implementazioni per chunking, parsing YAML

import logging
logger = logging.getLogger("modular-2")

class WordChunkSplitter(BaseTextSplitter):
    """Splitter che divide il testo in chunk di N parole."""
    def __init__(self, chunk_size=50):
        self.chunk_size = chunk_size
    def split(self, text):
        words = text.split()
        return [' '.join(words[i:i+self.chunk_size]) for i in range(0, len(words), self.chunk_size)]

class LineSplitter(BaseTextSplitter):
    """Splitter che divide il testo per righe."""
    def split(self, text):
        return text.splitlines()
