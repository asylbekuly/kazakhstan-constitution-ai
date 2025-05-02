# vector_store.py

import chromadb
from sentence_transformers import SentenceTransformer

class ConstitutionVectorStore:
    def __init__(self, collection_name="constitution"):
        self.client = chromadb.Client()
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, documents: list[str]):
        embeddings = self.embedding_model.encode(documents).tolist()
        for idx, (doc, emb) in enumerate(zip(documents, embeddings)):
            self.collection.add(
                documents=[doc],
                embeddings=[emb],
                ids=[f"doc_{idx}"]
            )
        print(f"✅ Added {len(documents)} documents to ChromaDB.")

    def search(self, query: str, n_results: int = 3):
        query_embedding = self.embedding_model.encode([query]).tolist()
        results = self.collection.query(
            query_embeddings=query_embedding,
            n_results=n_results
        )
        return results["documents"][0]
