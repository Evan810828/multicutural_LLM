# RAG Pipeline for Multicultural LLM

## Quick Start

### 1. Data Setup

**Download the dataset** from [Google Drive](https://drive.google.com/drive/folders/15ApysYrGPHzfXsLnPJ0tRL4qYC0oE0_b?usp=sharing) and place the files in:

```
multicultural_llm/data/raw/
```

The training materials should be in DOCX or TXT format. Personal stories or files you want to exclude should go in `data/excluded/`.

### 2. Install Dependencies

```bash
pip install -r requirements.txt

# Set your OpenAI API key
export OPENAI_API_KEY='your-api-key-here'
```

### 3. Process Data and Build Index

```bash
python src/ingest.py && python src/chunking.py && python src/embed_index.py
```

### 4. Run the Gradio UI

```bash
python src/gradio_app.py
```

Or query from command line:
```bash
python src/rag_answer.py
```

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

## Batch Inference for Case Study

Run batch inference on a CSV file of testing questions to compare static LLM vs RAG responses:

```bash
python src/batch_inference.py --input data/test_questions.csv --output results/case_study.csv
```

### Input CSV Format

The input CSV must contain a `question` column. Optional columns:
- `question_id`: Unique identifier for each question
- Any other metadata columns you want to preserve

The `question` column should contain the full user query, including any background information or context the user provides.

Example:
```csv
question_id,question
1,"What happens during a mammogram?"
2,"I'm a 45-year-old woman and my mother had breast cancer. Should I get screened more often?"
```

### Output CSV

The output CSV includes all original columns plus:
- `static_response`: Response from static LLM (no RAG context)
- `rag_response`: Response from RAG-augmented LLM
- `rag_sources`: Retrieved source documents (semicolon-separated)

### Command Line Options

```bash
python src/batch_inference.py --help

Options:
  --input, -i     Path to input CSV file (required)
  --output, -o    Path to output CSV file (default: results/case_study_YYYYMMDD_HHMMSS.csv)
  --quiet, -q     Disable progress bar
```
