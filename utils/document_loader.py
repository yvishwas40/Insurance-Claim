import fitz  # PyMuPDF

def extract_text(file_path: str) -> str:
    doc = fitz.open(file_path)
    return "\n".join(page.get_text() for page in doc)
