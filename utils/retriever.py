from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os

# ✅ Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# ✅ Initialize Pinecone client
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

# ✅ Connect to the existing index
index = pc.Index("hackrx-index")

# ✅ Query top-k chunks from Pinecone
def get_top_k_chunks_pinecone(query, namespace, top_k=5):
    query_vec = model.encode([query]).tolist()[0]

    response = index.query(
        vector=query_vec,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )

    print("DEBUG - Pinecone Response:", response)

    matches = []
    for match in response['matches']:
        metadata = match.get('metadata', {})
        text = metadata.get('text')
        if text:
            matches.append(text)
        else:
            print("Warning: 'text' field missing in metadata:", metadata)

    return matches
