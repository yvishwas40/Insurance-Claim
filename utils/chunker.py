def chunk_text(text: str, chunk_size: int = 500) -> list:
    words = text.split()
    return [' '.join(words[i:i+chunk_size]) for i in range(0, len(words), chunk_size)]
