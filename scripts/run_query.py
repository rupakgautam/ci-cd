"""Query the RAG system with hybrid search, reranking, and citation enforcement."""

import os
import sys

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from llm.answer_generator import generate_answer
from retrieval.hybrid_search import hybrid_search
from retrieval.reranker import rerank


def run_query(query):
    """Run a query through the full RAG pipeline.

    Returns a dict with:
      - answer: the generated answer text
      - citations: list of citation objects
      - retrieved_docs: the reranked documents used as context
    """
    docs = hybrid_search(query)
    reranked_docs = rerank(query, docs)

    context_parts = []
    for doc in reranked_docs:
        source = os.path.basename(doc["source"])
        page = doc["page"]
        context_parts.append(f"[Source: {source}, Page: {page}]\n{doc['text']}")

    context = "\n\n".join(context_parts)
    result = generate_answer(query, context)

    return {
        "answer": result["answer"],
        "citations": result["citations"],
        "retrieved_docs": reranked_docs,
        "raw_response": result.get("raw", "")
    }


def main():
    query = input("Ask question: ")
    result = run_query(query)

    print("\n" + "=" * 60)
    print("ANSWER:")
    print("=" * 60)
    print(result["answer"])

    if result["citations"]:
        print("\n" + "-" * 60)
        print("CITATIONS:")
        print("-" * 60)
        for i, cite in enumerate(result["citations"], 1):
            source = cite.get("source", "unknown")
            page = cite.get("page", "?")
            quote = cite.get("quote", "")
            print(f"  [{i}] {source}, Page {page}")
            if quote:
                print(f"      \"{quote[:100]}...\"" if len(quote) > 100 else f"      \"{quote}\"")


if __name__ == "__main__":
    main()
