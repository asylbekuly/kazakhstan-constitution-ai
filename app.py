import streamlit as st
import json
from document_loader import load_constitution_text, split_text_to_chunks
from vector_store import ConstitutionVectorStore
from llm_interface import ask_ollama
from datetime import datetime

# --- UI настройки ---
st.set_page_config(page_title="Kazakhstan Constitution AI Assistant", layout="wide")
st.title("📜 AI Assistant for Constitution of the Republic of Kazakhstan")
st.markdown("Ask questions about the Constitution or your uploaded documents below:")

# --- Инициализация хранилища векторов с Конституцией ---
@st.cache_resource
def init_vector_store():
    text = load_constitution_text("constitution_data/constitution.txt")
    chunks = split_text_to_chunks(text)
    store = ConstitutionVectorStore()
    store.add_documents(chunks)
    return store

store = init_vector_store()

# --- Загрузка файлов пользователем (ВЫШЕ вопроса) ---
uploaded_files = st.file_uploader(
    "📎 Upload your own documents (PDF, DOCX, or TXT):",
    type=["pdf", "docx", "txt"],
    accept_multiple_files=True
)

uploaded_docs = []

if uploaded_files:
    for uploaded_file in uploaded_files:
        file_bytes = uploaded_file.read()
        file_name = uploaded_file.name

        if file_name.endswith(".txt"):
            text = file_bytes.decode("utf-8")
        elif file_name.endswith(".pdf"):
            import fitz
            with fitz.open(stream=file_bytes, filetype="pdf") as doc:
                text = "\n".join([page.get_text() for page in doc])
        elif file_name.endswith(".docx"):
            from docx import Document
            from io import BytesIO
            doc = Document(BytesIO(file_bytes))
            text = "\n".join([p.text for p in doc.paragraphs])
        else:
            st.warning(f"❌ Unsupported file type: {file_name}")
            continue

        uploaded_docs.append(text)
        st.success(f"✅ Uploaded: {file_name}")

# --- Индексация загруженных документов ---
if uploaded_docs:
    all_chunks = []
    for doc_text in uploaded_docs:
        chunks = split_text_to_chunks(doc_text)
        all_chunks.extend(chunks)

    if all_chunks:
        store.add_documents(all_chunks)
        st.success(f"🔎 Indexed {len(all_chunks)} chunks from uploaded documents.")

# --- Поле для ввода вопроса ---
user_question = st.text_input("💬 Your Question")

# --- Логирование вопросов и ответов ---
def log_interaction(question, answer, filepath="query_log.json"):
    entry = {
        "timestamp": datetime.now().isoformat(),
        "question": question,
        "answer": answer
    }

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)
    except (FileNotFoundError, json.decoder.JSONDecodeError):
        data = []

    data.append(entry)

    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)


# --- Обработка вопроса ---
if st.button("Get Answer"):
    if not user_question.strip():
        st.warning("Please enter a question.")
    else:
        with st.spinner("Searching relevant content..."):
            if uploaded_docs:
                context = "\n\n".join(uploaded_docs)
            else:
                context_chunks = store.search(user_question, n_results=5)
                context = "\n\n".join(context_chunks)
            answer = ask_ollama(context, user_question)
        st.success("✅ Answer:")
        st.markdown(answer)
        log_interaction(user_question, answer)
if st.button("📂 Show all documents in ChromaDB"):
    docs = store.collection.get()["documents"]
    st.code("\n\n---\n\n".join(docs[:5]), language="markdown")
