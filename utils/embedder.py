# utils/embedder.py

import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer

# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Pinecone client
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment="gcp-starter"
)

index_name = "hackrx-index"

# ✅ Create index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # all-MiniLM-L6-v2 has 384 dims
        metric="cosine",
        spec=ServerlessSpec(cloud="aws", region="us-east-1")
    )

# ✅ Connect to index
index = pc.Index(index_name)

# ✅ Load model once
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Embed and upsert chunks
def embed_chunks_pinecone(chunks, namespace="default"):
    vectors = model.encode([chunk["text"] for chunk in chunks]).tolist()

    upsert_payload = []
    for i, vector in enumerate(vectors):
        metadata = {
            "chunk_id": i,
            "text": chunks[i]["text"][:400]
        }
        upsert_payload.append({
            "id": f"chunk-{i}",
            "values": vector,
            "metadata": metadata
        })

    index.upsert(vectors=upsert_payload, namespace=namespace)
    print("Upserting", len(upsert_payload), "chunks")
