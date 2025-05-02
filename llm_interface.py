# llm_interface.py

import requests

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3.2"


def ask_ollama(context: str, question: str) -> str:
    prompt = f"""You are an assistant that answers questions based on the Constitution of Kazakhstan.
Use the following context to answer the question.

Context:
{context}

Question:
{question}

Answer:"""

    response = requests.post(OLLAMA_URL, json={
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False
    })

    if response.status_code == 200:
        return response.json()["response"].strip()
    else:
        return f"⚠️ Error from Ollama: {response.status_code}\n{response.text}"
