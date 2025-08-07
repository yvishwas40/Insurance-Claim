import google.generativeai as genai
import os
import json

genai.configure(api_key=os.getenv("GEMINI_API_KEY"))

def get_structured_answer(chunks, question):
    import re
    # Extract text from each chunk
    context_text = '\n'.join(chunk["text"] for chunk in chunks)
    prompt = f"""
You are an expert in insurance policy documents.

Based only on the provided policy document context, answer the user's question as structured JSON. If the answer is not found in the context, say "Sorry, no relevant information found in the policy to answer your question." and leave the clause_reference blank.

Context:
{context_text}

Question:
{question}

Return your response in this exact JSON format:

{{
  "answer": "...",               
  "reasoning": "...",            
  "clause_reference": "..."      
}}
"""

    model = genai.GenerativeModel("gemini-1.5-flash")
    response = model.generate_content(prompt)
    raw_text = response.text.strip()

    def clean_json_response(raw_text):
        raw_text = re.sub(r"```(json)?", "", raw_text).strip()
        try:
            return json.loads(raw_text)
        except json.JSONDecodeError:
            try:
                return json.loads(raw_text.replace("'", '"'))
            except Exception as e:
                raise ValueError(f"Failed to parse model response:\n{raw_text}") from e

    return clean_json_response(raw_text)