# document_loader.py

from langchain.text_splitter import RecursiveCharacterTextSplitter
from vector_store import ConstitutionVectorStore

def load_constitution_text(filepath: str) -> str:
    with open(filepath, "r", encoding="utf-8") as file:
        return file.read()

def split_text_to_chunks(text: str, chunk_size: int = 500, chunk_overlap: int = 100):
    splitter = RecursiveCharacterTextSplitter(
        chunk_size=chunk_size,
        chunk_overlap=chunk_overlap
    )
    return splitter.split_text(text)

if __name__ == "__main__":
    path = "constitution_data/constitution.txt"
    text = load_constitution_text(path)
    chunks = split_text_to_chunks(text)
    print(f"Loaded {len(chunks)} chunks.")
    print(chunks[:2])  

 
    store = ConstitutionVectorStore()
    store.add_documents(chunks)

    results = store.search("What is the form of government?")
    print("\n🔍 Search Results:")
    for res in results:
        print("-", res)
