"""
memory.py - Moduli di memoria conversazionale e buffer

- Gestiscono la memoria condivisa tra agenti, pipeline o step.
- Permettono di salvare, recuperare e aggiornare lo stato della conversazione o dati temporanei.
- Possono essere associati a uno o più agenti/pipeline tramite configurazione YAML.

Consulta la documentazione inline per dettagli su come estendere la memoria o implementare nuovi tipi di memory.
"""

"""
Memory: Gestione contesto e stato conversazione.
"""

import logging
logger = logging.getLogger("modular-2")

class BaseMemory:
    """Interfaccia base per la memoria."""
    def load(self, session_id):
        raise NotImplementedError
    def save(self, session_id, data):
        raise NotImplementedError

class ConversationMemory(BaseMemory):
    """Memoria conversazionale semplice (in RAM)."""
    def __init__(self):
        self.sessions = {}
    def load(self, session_id):
        return self.sessions.get(session_id, [])
    def save(self, session_id, data):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(data)
        logger.debug(f"[Memory] Saved for session {session_id}: {data}")

class BufferMemory(BaseMemory):
    """Memoria a buffer limitato (es. ultimi N turni)."""
    def __init__(self, maxlen=10):
        self.sessions = {}
        self.maxlen = maxlen
    def load(self, session_id):
        return self.sessions.get(session_id, [])
    def save(self, session_id, data):
        if session_id not in self.sessions:
            self.sessions[session_id] = []
        self.sessions[session_id].append(data)
        if len(self.sessions[session_id]) > self.maxlen:
            self.sessions[session_id] = self.sessions[session_id][-self.maxlen:]
        logger.debug(f"[Memory] Buffer saved for session {session_id}: {data}")

# TODO: Implementazioni per memoria conversazionale, sessioni dinamiche
