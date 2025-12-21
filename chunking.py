def chunk_text(text, max_chars=500):
    """
    Splits text into chunks without breaking meaning.
    """
    chunks = []
    start = 0

    while start < len(text):
        end = start + max_chars
        chunks.append(text[start:end].strip())
        start = end

    return chunks
