# utils/embedder.py

import os
from pinecone import Pinecone, ServerlessSpec
from dotenv import load_dotenv
from sentence_transformers import SentenceTransformer


# ✅ Load environment variables
load_dotenv()

# ✅ Initialize Pinecone client with correct environment for free tier
pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY"),
    environment="gcp-starter"  # ✅ Must match the region below
)

index_name = "hackrx-index"

# ✅ Create the index if it doesn't exist
if index_name not in pc.list_indexes().names():
    pc.create_index(
        name=index_name,
        dimension=384,  # Depends on your embedding model
        metric="cosine",  # or "dotproduct", "euclidean"
        spec=ServerlessSpec(cloud="aws", region="us-east-1")  # ✅ Free tier-compatible
    )

# ✅ Connect to the index
index = pc.Index(index_name)

# ✅ Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Embed and upsert function
def embed_chunks_pinecone(chunks, namespace="default"):
    from sentence_transformers import SentenceTransformer
    import os
    from pinecone import Pinecone

    model = SentenceTransformer("all-MiniLM-L6-v2")

    pc = Pinecone(
        api_key=os.getenv("PINECONE_API_KEY"),
        environment="gcp-starter"
    )
    index = pc.Index(index_name)

    vectors = model.encode(chunks).tolist()

    upsert_payload = []
    for i, vector in enumerate(vectors):
        metadata = {
            "chunk_id": i,
            "text": chunks[i]["text"][:400] # ✅ truncate to safe limit (max ~400 chars)
        }
        upsert_payload.append({
            "id": f"chunk-{i}",
            "values": vector,
            "metadata": metadata
        })

    index.upsert(vectors=upsert_payload, namespace=namespace)
    print("Upserting", len(upsert_payload), "chunks")


# Example usage
# index.upsert(vectors=[...])
