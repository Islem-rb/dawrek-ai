from sentence_transformers import SentenceTransformer
import numpy as np

MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"

model = None

def get_model():
    global model
    if model is None:
        print(f"Loading embedding model: {MODEL_NAME}")
        model = SentenceTransformer(MODEL_NAME)
    return model

def embed_text(text: str) -> list[float]:
    m = get_model()
    embedding = m.encode(text, normalize_embeddings=True)
    return embedding.tolist()

def embed_texts(texts: list[str]) -> list[list[float]]:
    m = get_model()
    embeddings = m.encode(texts, normalize_embeddings=True)
    return embeddings.tolist()
