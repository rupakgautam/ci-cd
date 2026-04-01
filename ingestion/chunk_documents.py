def chunk_text(pages, chunk_size=700, overlap=100):
    """Split pages into overlapping text chunks."""
    chunks = []

    for page_data in pages:
        text = page_data["text"]
        page_num = page_data["page"]
        start = 0

        while start < len(text):
            end = start + chunk_size
            chunk = text[start:end]
            chunks.append({"text": chunk, "page": page_num})
            start += chunk_size - overlap

    return chunks
