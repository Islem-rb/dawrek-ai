from groq import Groq
import os

_client = None

def get_client():
    global _client
    if _client is None:
        _client = Groq(api_key=os.getenv("GROQ_API_KEY"))
    return _client

SYSTEM_PROMPT = """You are a smart assistant for Dawrek, a patient queue management system.

CRITICAL LANGUAGE RULE:
- If the user writes in French → respond ONLY in French
- If the user writes in Tunisian Darija (تونسي) → respond ONLY in Tunisian Darija
- If the user writes in Arabic (عربي فصيح) → respond ONLY in Modern Standard Arabic
- Detect the language from the user's message and match it exactly. Never switch languages.

Answer ONLY based on the context provided. If the answer is not in the context, say so clearly in the user's language.
Be concise, clear, and helpful."""

def generate_response(query: str, context_chunks: list[dict]) -> str:
    context = "\n\n".join([f"[{c['source']}]\n{c['text']}" for c in context_chunks])

    user_message = f"""Context:
{context}

Patient question: {query}"""

    response = get_client().chat.completions.create(
        model="llama-3.1-8b-instant",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_message}
        ],
        temperature=0.3,
        max_tokens=512
    )
    return response.choices[0].message.content
