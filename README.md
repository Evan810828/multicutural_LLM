# Privacy-First RAG Pipeline (Multicultural LLM)

This folder contains a privacy-first Retrieval-Augmented Generation (RAG) pipeline for breast cancer education content. It follows the implementation plan and **excludes personal stories** from the index.

## Structure

```
multicultural_llm/
  data/
    raw/                  # place training materials here (DOCX/TXT)
    excluded/             # personal stories or rejected files
    processed/
      docs.jsonl
      chunks.jsonl
  index/
    faiss.index
    metadata.parquet
  results/
  src/
```

> Note: If `data/raw` is empty, ingestion will also scan `data/` and skip `excluded/` and `processed/`.

## Setup

1. Create and activate a Python environment.
2. Install dependencies from `requirements.txt`.
3. Set `OPENAI_API_KEY` in your environment.

## Runbook

1. Ingest files:
   - `python src/ingest.py`
2. Chunk and apply privacy gate:
   - `python src/chunking.py`
3. Build index:
   - `python src/embed_index.py`
4. Ask a question:
   - `python src/rag_answer.py`
5. Evaluate static vs RAG:
   - `python src/eval.py`

## Gradio UI

Run the Gradio app:

- `python src/gradio_app.py`

## API (Optional)

Run the API server:

- `uvicorn src.api:app --reload`

POST to `/answer` with JSON:

```json
{"question": "What happens during a mammogram?", "use_rag": true}
```
