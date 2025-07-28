from sentence_transformers import SentenceTransformer
from pinecone import Pinecone
import os

model = SentenceTransformer("all-MiniLM-L6-v2")
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.Index("hackrx-index")

def get_top_k_chunks_pinecone(query, namespace, top_k=5):
    query_vec = model.encode([query]).tolist()[0]
    response = index.query(
        vector=query_vec,
        top_k=top_k,
        include_metadata=True,
        namespace=namespace
    )

    print("DEBUG - Pinecone Response:", response)  # Add this line

    matches = []
    for match in response['matches']:
        metadata = match.get('metadata', {})
        text = metadata.get('text')
        if text:
            matches.append(text)
        else:
            print("Warning: 'text' field missing in metadata:", metadata)

    return matches
