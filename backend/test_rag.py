import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from dotenv import load_dotenv
load_dotenv()

from backend.rag.retriever import retrieve
from backend.rag.generator import generate_response

test_queries = [
    "قداش باقي في الطابور؟",           # Darija
    "شنوة الوراق اللي محتاجهم؟",        # Darija
    "Combien de temps dois-je attendre?" # French
]

for query in test_queries:
    print(f"\n{'='*50}")
    print(f"Query: {query}")
    chunks = retrieve(query, top_k=2)
    print(f"Retrieved {len(chunks)} chunks from: {[c['source'] for c in chunks]}")
    response = generate_response(query, chunks)
    print(f"Response:\n{response}")
