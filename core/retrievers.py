"""
retrievers.py - Moduli per retrieval semantico/documentale (RAG, vector DB, ecc.)

- Permettono di cercare documenti simili, chunk di testo o knowledge base.
- Possono essere usati da agenti, chain o pipeline.
- Supportano l'integrazione con LLM per Retrieval Augmented Generation (RAG).

Consulta la documentazione inline per dettagli su come aggiungere nuovi retrievers o estendere la logica.
"""

import logging
logger = logging.getLogger("modular-2")

class BaseRetriever:
    """Interfaccia base per retrievers."""
    def retrieve(self, query):
        raise NotImplementedError

class SemanticRetriever(BaseRetriever):
    """Retriever semantico: usa vector DB se disponibile, fallback stub."""
    def __init__(self, vector_db=None, config=None):
        self.vector_db = vector_db
        self.config = config or {}
        self._chroma = None
        try:
            import chromadb
            self._chroma = chromadb.Client()
        except ImportError:
            self._chroma = None
    def retrieve(self, query):
        logger.info(f"[Retriever] Semantic search for: {query}")
        if self._chroma:
            # Esempio: cerca in una collection chiamata 'semantic_docs'
            collection = self._chroma.get_or_create_collection("semantic_docs")
            # Fallback: usa hash come embedding
            import hashlib
            embedding = [float(int(hashlib.md5(query.encode()).hexdigest(), 16) % 1000)] * 384
            results = collection.query(query_embeddings=[embedding], n_results=3)
            return results.get('documents', [])
        return [f"Stub result for: {query}"]

class ChromaDBRetriever(BaseRetriever):
    """Retriever che usa ChromaDB come vector store per RAG, con embedding LLM reale (sentence-transformers)."""
    def __init__(self, persist_directory="chroma_db", embedding_fn=None, model_name="all-MiniLM-L6-v2"):
        try:
            import chromadb
            from chromadb.config import Settings
        except ImportError:
            raise ImportError("Devi installare chromadb: pip install chromadb")
        self.chroma_client = chromadb.Client(Settings(persist_directory=persist_directory))
        self.collection = self.chroma_client.get_or_create_collection("rag_docs")
        self.model_name = model_name
        self.embedding_fn = embedding_fn or self.default_embedding
        self._embedding_model = None

    def default_embedding(self, text):
        try:
            if self._embedding_model is None:
                from sentence_transformers import SentenceTransformer
                self._embedding_model = SentenceTransformer(self.model_name)
            return self._embedding_model.encode(text).tolist()
        except ImportError:
            import hashlib
            return [float(int(hashlib.md5(text.encode()).hexdigest(), 16) % 1000)] * 384

    def add_documents(self, docs, metadatas=None):
        metadatas = metadatas or [{} for _ in docs]
        embeddings = [self.embedding_fn(doc) for doc in docs]
        ids = [f"doc_{i}" for i in range(len(docs))]
        self.collection.add(documents=docs, embeddings=embeddings, metadatas=metadatas, ids=ids)
        logger.info(f"[ChromaDBRetriever] {len(docs)} documenti indicizzati.")

    def retrieve(self, query, n_results=3):
        embedding = self.embedding_fn(query)
        results = self.collection.query(query_embeddings=[embedding], n_results=n_results)
        return results.get('documents', [])

class RAGRetriever(BaseRetriever):
    """Retriever per Retrieval Augmented Generation (usa un altro retriever e LLM opzionale)."""
    def __init__(self, retriever, llm=None):
        self.retriever = retriever
        self.llm = llm
    def retrieve(self, query):
        docs = self.retriever.retrieve(query)
        if self.llm:
            # Esempio: prompta l'LLM con i documenti
            prompt = f"Rispondi usando questi documenti:\n{docs}\nDomanda: {query}"
            return self.llm.generate(prompt)
        return docs

# TODO: Implementazioni per vector DB, RAG, parsing YAML
