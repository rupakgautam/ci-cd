"""BM25 keyword search over ChromaDB document store.

Builds a BM25 index once and caches it for repeated queries.
Call rebuild_index() after ingesting new documents.
"""

import re

import chromadb
from rank_bm25 import BM25Okapi

_PUNCTUATION_RE = re.compile(r"[^\w\s]", re.UNICODE)

# --- Module-level cache ---
_bm25_index = None
_cached_documents = None
_cached_metadatas = None


def tokenize(text):
    """Lowercase, strip punctuation, and split on whitespace."""
    text = text.lower()
    text = _PUNCTUATION_RE.sub("", text)
    return text.split()


def _get_all_documents():
    """Fetch every document and its metadata from ChromaDB."""
    client = chromadb.PersistentClient(path="./chroma_db")
    collection = client.get_or_create_collection("documents")
    results = collection.get(include=["documents", "metadatas"])
    return results["documents"], results["metadatas"]


def _ensure_index():
    """Build the BM25 index if it hasn't been built yet."""
    global _bm25_index, _cached_documents, _cached_metadatas

    if _bm25_index is not None:
        return

    documents, metadatas = _get_all_documents()
    if not documents:
        _cached_documents = []
        _cached_metadatas = []
        return

    tokenized_docs = [tokenize(doc) for doc in documents]
    _bm25_index = BM25Okapi(tokenized_docs)
    _cached_documents = documents
    _cached_metadatas = metadatas


def rebuild_index():
    """Force-rebuild the BM25 index (call after ingesting new docs)."""
    global _bm25_index
    _bm25_index = None
    _ensure_index()


def bm25_search(query, top_k=5):
    """Search documents using BM25 keyword matching.

    Args:
        query: The search query string.
        top_k: Maximum number of results to return.

    Returns:
        List of dicts with keys: text, source, page, score.
    """
    _ensure_index()

    if not _cached_documents:
        return []

    tokenized_query = tokenize(query)
    scores = _bm25_index.get_scores(tokenized_query)

    # Pair documents with scores and filter out zero-score (irrelevant) results
    ranked = sorted(
        zip(_cached_documents, _cached_metadatas, scores),
        key=lambda x: x[2],
        reverse=True,
    )

    return [
        {
            "text": doc,
            "source": meta.get("source", ""),
            "page": meta.get("page", "?"),
            "score": float(score),
        }
        for doc, meta, score in ranked[:top_k]
        if score > 0
    ]
