from retrieval.bm25_search import bm25_search
from retrieval.vector_search import search as vector_search


def hybrid_search(query):

    vector_results = vector_search(query, top_k=5)

    bm25_results = bm25_search(query, top_k=5)

    combined = vector_results + bm25_results

    seen = set()
    unique_results = []
    for item in combined:
        if item["text"] not in seen:
            seen.add(item["text"])
            unique_results.append(item)

    return unique_results
