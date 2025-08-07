from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List
import tempfile
import requests
import os
import traceback

from utils.document_loader import extract_text
from utils.chunker import chunk_text
from utils.embedder import embed_chunks_pinecone  
from utils.retriever import get_top_k_chunks_pinecone  
from utils.llm_engine import get_structured_answer 

app = FastAPI()

class QueryRequest(BaseModel):
    documents: str
    questions: List[str]

@app.post("/api/v1/hackrx/run")
async def run_query(payload: QueryRequest):
    try:
        # 1. Download the document
        response = requests.get(payload.documents)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Unable to download document.")

        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as tmp:
            tmp.write(response.content)
            doc_path = tmp.name

        # 2. Extract full text from document
        full_text = extract_text(doc_path)

        # 3. Chunk the text
        chunks = [{"text": c} for c in chunk_text(full_text)]

        # 4. Embed and upsert into Pinecone
        namespace_id = "hackrx-session"
        embed_chunks_pinecone(chunks, namespace=namespace_id)  # ✅ include namespace
        

        # 5. Process each question
        results = []
        for question in payload.questions:
            top_chunks = get_top_k_chunks_pinecone(question, namespace=namespace_id)  # ✅ fixed call

            # 6. Get structured answer using LLM
            structured = get_structured_answer(top_chunks, question)

            results.append({
                "answer": structured.get("answer"),
                # 
                # "confidence": structured.get("confidence", 0.0)
            })

        return {
            "results": results
        }

    except Exception as e:
        traceback.print_exc()
        raise HTTPException(status_code=500, detail=f"Internal Error: {str(e)}")

@app.get("/")
def read_root():
    return {"message": "Welcome to the Insurance Query Retrieval API 🚀"}
if __name__ == "__main__":
    import uvicorn
    port = int(os.environ.get("PORT", 8080))
    uvicorn.run("main:app", host="0.0.0.0", port=port)
