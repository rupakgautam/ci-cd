"""FastAPI wrapper for the RAG pipeline."""

import glob
import os
import sys

from fastapi import FastAPI, File, HTTPException, UploadFile
from pydantic import BaseModel

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from ingestion.chunk_documents import chunk_text
from ingestion.create_embeddings import store_chunks
from ingestion.load_pdf import load_pdf
from scripts.run_query import run_query

app = FastAPI(
    title="RAG API",
    description="Local RAG system powered by Ollama + ChromaDB",
    version="1.0.0",
)


class QueryRequest(BaseModel):
    question: str


class QueryResponse(BaseModel):
    answer: str
    citations: list
    retrieved_docs: list


@app.get("/health")
def health():
    return {"status": "ok"}


@app.post("/query", response_model=QueryResponse)
def query(request: QueryRequest):
    if not request.question.strip():
        raise HTTPException(status_code=400, detail="Question cannot be empty")
    result = run_query(request.question)
    return QueryResponse(
        answer=result["answer"],
        citations=result["citations"],
        retrieved_docs=result["retrieved_docs"],
    )


@app.post("/ingest")
async def ingest(file: UploadFile = File(...)):
    """Upload and ingest a PDF into the vector store."""
    if not file.filename.endswith(".pdf"):
        raise HTTPException(status_code=400, detail="Only PDF files are supported")

    save_dir = "data/raw_docs"
    os.makedirs(save_dir, exist_ok=True)
    save_path = os.path.join(save_dir, file.filename)

    contents = await file.read()
    with open(save_path, "wb") as f:
        f.write(contents)

    pages = load_pdf(save_path)
    chunks = chunk_text(pages)
    store_chunks(chunks, file_id=save_path)

    return {"message": f"Ingested {len(chunks)} chunks from '{file.filename}'"}


@app.post("/ingest/scan")
def ingest_scan():
    """Re-ingest all PDFs already in data/raw_docs/."""
    pdf_files = glob.glob("data/raw_docs/*.pdf")
    if not pdf_files:
        raise HTTPException(status_code=404, detail="No PDFs found in data/raw_docs/")

    total_chunks = 0
    for pdf_path in pdf_files:
        pages = load_pdf(pdf_path)
        chunks = chunk_text(pages)
        store_chunks(chunks, file_id=pdf_path)
        total_chunks += len(chunks)

    return {"message": f"Ingested {total_chunks} chunks from {len(pdf_files)} PDFs"}
