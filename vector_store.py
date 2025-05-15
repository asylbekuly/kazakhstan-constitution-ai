import chromadb
from sentence_transformers import SentenceTransformer
from vector_store_onchain import add_vector

class ConstitutionVectorStore:
    def __init__(self, collection_name="constitution"):
        self.client = chromadb.Client()
        self.embedding_model = SentenceTransformer("all-MiniLM-L6-v2")
        self.collection = self.client.get_or_create_collection(name=collection_name)

    def add_documents(self, documents: list[str]):
        try:
            embeddings = self.embedding_model.encode(documents).tolist()
            for idx, (doc, emb) in enumerate(zip(documents, embeddings)):
                doc_id = f"doc_{idx}"
                self.collection.add(
                    documents=[doc],
                    embeddings=[emb],
                    ids=[doc_id]
                )
                try:
                    add_vector(doc_id, doc, emb)
                except Exception as e:
                    print(f"⚠️ Не удалось сохранить doc_{idx} в блокчейн: {e}")
            print(f"✅ Добавлено {len(documents)} документов в ChromaDB и блокчейн.")
        except Exception as e:
            print(f"❌ Ошибка при добавлении документов: {e}")
            raise

    def search(self, query: str, n_results: int = 3):
        try:
            query_embedding = self.embedding_model.encode([query]).tolist()
            results = self.collection.query(
                query_embeddings=query_embedding,
                n_results=n_results
            )
            return results["documents"][0]
        except Exception as e:
            print(f"❌ Ошибка при поиске: {e}")
            return []