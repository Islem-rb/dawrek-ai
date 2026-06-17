import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from backend.rag.retriever import ingest_documents

if __name__ == "__main__":
    docs_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "knowledge_base")
    print(f"Ingesting documents from: {docs_path}")
    ingest_documents(docs_path)
    print("Done.")
