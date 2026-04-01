# RAG System with Ollama & ChromaDB

A production-ready Retrieval-Augmented Generation system that answers questions from a document knowledge base with **enforced citations**.

## Architecture

```
Documents (PDF/MD/Web) → Chunking → Embeddings → ChromaDB
                                                      ↓
               User Query → Hybrid Search (Vector + BM25)
                                                      ↓
                              Cross-Encoder Reranking → Top K chunks
                                                      ↓
                              Ollama LLM → Structured Answer + Citations
```

## Stack

| Component | Technology |
|-----------|-----------|
| LLM | Ollama (llama3) |
| Vector Store | ChromaDB |
| Embeddings | SentenceTransformers (all-MiniLM-L6-v2) |
| Reranking | CrossEncoder (ms-marco-MiniLM-L-6-v2) |
| Keyword Search | BM25 (rank-bm25) |

## Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Make sure Ollama is running with llama3
ollama pull llama3
```

## Usage

### 1. Ingest Documents

Place PDFs or Markdown files in `data/raw_docs/`, then run:

```bash
python scripts/ingest_pipeline.py
```

To ingest web pages:

```bash
python scripts/ingest_pipeline.py --urls https://example.com/page1 https://example.com/page2
```

### 2. Query

```bash
python scripts/run_query.py
```

The system returns structured answers with citations:

```
ANSWER:
The document describes... (Source: data.pdf, Page: 3)

CITATIONS:
  [1] data.pdf, Page 3
      "exact quote from the source..."
```

## Configuration

All settings are in `config/settings.yaml`:

```yaml
ingestion:
  chunk_size: 700
  chunk_overlap: 100

retrieval:
  vector_top_k: 5
  bm25_top_k: 5
  reranker_top_k: 5

llm:
  model: "llama3"
  prompt_version: "v2"  # v1 = free text, v2 = structured JSON
```

## Evaluation

### Run Evaluation

```bash
# Full eval with LLM-as-judge for faithfulness
python evaluation/run_eval.py

# Faster eval using heuristic faithfulness (no Ollama needed)
python evaluation/run_eval.py --no-llm
```

### Metrics

| Metric | Description | Threshold |
|--------|-------------|-----------|
| Retrieval Precision | Fraction of retrieved docs from expected sources | 0.6 |
| Citation Coverage | Fraction of expected sources cited in the answer | 0.7 |
| Faithfulness | Whether the answer is grounded in the context | 0.7 |

### CI Integration

Evaluation runs automatically via GitHub Actions on push/PR to `main`. Builds fail if metrics drop below thresholds.

## Project Structure

```
├── config/
│   ├── settings.yaml          # All tunable parameters
│   └── config_loader.py       # Config access with dot notation
├── ingestion/
│   ├── load_pdf.py            # PDF document loader
│   ├── load_markdown.py       # Markdown document loader
│   ├── load_webpage.py        # Web page loader
│   ├── chunk_documents.py     # Text chunking with overlap
│   └── create_embeddings.py   # Embedding + ChromaDB storage
├── retrieval/
│   ├── vector_search.py       # Semantic vector search
│   ├── bm25_search.py         # BM25 keyword search
│   ├── hybrid_search.py       # Combined vector + BM25
│   └── reranker.py            # Cross-encoder reranking
├── llm/
│   └── answer_generator.py    # LLM answer generation + JSON parsing
├── prompts/
│   ├── rag_prompt_v1.txt      # Free-text citation prompt
│   ├── rag_prompt_v2.txt      # Structured JSON output prompt
│   └── prompt_changelog.md    # Version history
├── evaluation/
│   ├── golden_dataset.json    # 50 Q&A pairs
│   ├── metrics.py             # 3 evaluation metrics
│   └── run_eval.py            # Evaluation runner
├── scripts/
│   ├── ingest_pipeline.py     # Document ingestion CLI
│   └── run_query.py           # Query CLI
├── tests/
│   └── test_rag.py            # Unit tests
└── .github/workflows/
    └── eval_ci.yml            # CI evaluation workflow
```

## Tests

```bash
pytest tests/ -v
```
