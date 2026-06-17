from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct
from .embedder import embed_text
import os
import uuid

QDRANT_HOST = os.getenv("QDRANT_HOST", "localhost")
QDRANT_PORT = int(os.getenv("QDRANT_PORT", 6333))
COLLECTION_NAME = "dawrek_knowledge"
VECTOR_SIZE = 384

client = None

def get_client():
    global client
    if client is None:
        client = QdrantClient(host=QDRANT_HOST, port=QDRANT_PORT)
    return client

def init_collection(force_recreate=False):
    c = get_client()
    existing = [col.name for col in c.get_collections().collections]
    if COLLECTION_NAME in existing:
        if force_recreate:
            c.delete_collection(COLLECTION_NAME)
            print(f"Deleted existing collection '{COLLECTION_NAME}'.")
        else:
            print(f"Collection '{COLLECTION_NAME}' already exists.")
            return
    c.create_collection(
        collection_name=COLLECTION_NAME,
        vectors_config=VectorParams(size=VECTOR_SIZE, distance=Distance.COSINE)
    )
    print(f"Collection '{COLLECTION_NAME}' created.")

def parse_sections(content: str) -> list[dict]:
    """Parse a knowledge base file into labeled language sections."""
    sections = []
    current_lang = None
    current_lines = []

    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith("--- ") and stripped.endswith(" ---"):
            if current_lang and current_lines:
                sections.append({
                    "lang": current_lang,
                    "text": "\n".join(current_lines).strip()
                })
            current_lang = stripped.replace("---", "").strip()
            current_lines = []
        else:
            if current_lang:
                current_lines.append(line)

    if current_lang and current_lines:
        sections.append({
            "lang": current_lang,
            "text": "\n".join(current_lines).strip()
        })

    return sections

def ingest_documents(docs_path: str):
    c = get_client()
    init_collection(force_recreate=True)

    points = []
    for filename in os.listdir(docs_path):
        if not filename.endswith(".txt"):
            continue
        filepath = os.path.join(docs_path, filename)
        with open(filepath, "r", encoding="utf-8") as f:
            content = f.read().strip()

        sections = parse_sections(content)

        if not sections:
            # fallback: ingest whole file as one chunk
            vector = embed_text(content)
            points.append(PointStruct(
                id=str(uuid.uuid4()),
                vector=vector,
                payload={"text": content, "source": filename, "lang": "unknown"}
            ))
        else:
            for section in sections:
                if not section["text"]:
                    continue
                vector = embed_text(section["text"])
                points.append(PointStruct(
                    id=str(uuid.uuid4()),
                    vector=vector,
                    payload={"text": section["text"], "source": filename, "lang": section["lang"]}
                ))

    c.upsert(collection_name=COLLECTION_NAME, points=points)
    print(f"Ingested {len(points)} chunks into Qdrant.")

def retrieve(query: str, top_k: int = 3) -> list[dict]:
    c = get_client()
    query_vector = embed_text(query)
    results = c.search(
        collection_name=COLLECTION_NAME,
        query_vector=query_vector,
        limit=top_k
    )
    return [
        {
            "text": r.payload["text"],
            "source": r.payload["source"],
            "lang": r.payload.get("lang", "unknown"),
            "score": r.score
        }
        for r in results
    ]
