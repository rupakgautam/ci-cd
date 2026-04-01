Project: Local RAG System

Stack:
- Ollama for LLM
- ChromaDB for vector store
- SentenceTransformers for embeddings

Architecture:
1. Load PDF
2. Chunk documents
3. Store embeddings in Chroma
4. Retrieve top K chunks
5. Generate answer using Ollama

Rules:
- Always cite sources
- Only answer using retrieved context
- If context missing, say you do not know