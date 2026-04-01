"""Ingestion pipeline that loads PDFs, chunks them, and stores embeddings."""

import glob
import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from ingestion.chunk_documents import chunk_text
from ingestion.create_embeddings import store_chunks
from ingestion.load_pdf import load_pdf


def main():
    pdf_dir = "data/raw_docs"
    pdf_files = glob.glob(os.path.join(pdf_dir, "*.pdf"))

    for pdf_path in pdf_files:
        print(f"Loading: {pdf_path}")
        pages = load_pdf(pdf_path)
        chunks = chunk_text(pages)
        store_chunks(chunks, file_id=pdf_path)
        print(f"  Ingested {len(chunks)} chunks")

    print(f"\nIngestion complete — processed {len(pdf_files)} PDFs")


if __name__ == "__main__":
    main()
