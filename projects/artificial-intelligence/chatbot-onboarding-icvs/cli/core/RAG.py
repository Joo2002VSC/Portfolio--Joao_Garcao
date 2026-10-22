from ollama import chat
from .retrieval import retrieve_top_k
from .config import MODEL_NAME, TOP_K, TEMPERATURE

def answer_with_ollama_rag(question):
    hits = retrieve_top_k(question, TOP_K)

    context = "\n\n".join(
        [f"[{h['section']}]\n{h['text']}" for h in hits]
    )

    system_msg = (
        "You are a friendly ICVS chatbot assistant.\n"
        "Respond naturally, like talking to a helpful colleague.\n"
        "Use ONLY the provided context—don't add, assume, or invent anything.\n"
        "Make answers simple, direct, and engaging: start with 'Hey' or 'To get that...' and guide step-by-step if possible.\n"
        "If info is missing, say: 'Sorry, I don't have details on that in the docs.'\n"
        "Do not create hypothetical scenarios, puzzles, or stories—stick to the facts.\n"
        "Keep it short and chatty."
    )

    user_msg = (
        f"Context:\n{context}\n\n"
        f"Question: {question}\n\n"
        "Provide a helpful, conversational answer."
    )

    messages = [
        {"role": "system", "content": system_msg},
        {"role": "user", "content": user_msg}
    ]

    stream = chat(
        model=MODEL_NAME,
        messages=messages,
        stream=True,
        options={"temperature": 0.1}
    )

    answer = ""
    for chunk in stream:
        content = chunk.get("message", {}).get("content", "")
        print(content, end="", flush=True)
        answer += content

    print()
    return answer