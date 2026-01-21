from dataclasses import dataclass
from pathlib import Path


@dataclass
class Settings:
    project_root: Path = Path(__file__).resolve().parents[1]

    raw_dir: Path = project_root / "data" / "raw"
    excluded_dir: Path = project_root / "data" / "excluded"
    processed_dir: Path = project_root / "data" / "processed"
    index_dir: Path = project_root / "index"
    results_dir: Path = project_root / "results"

    docs_jsonl: Path = processed_dir / "docs.jsonl"
    chunks_jsonl: Path = processed_dir / "chunks.jsonl"

    faiss_index_path: Path = index_dir / "faiss.index"
    meta_path: Path = index_dir / "metadata.parquet"

    allow_doc_types = {
        "education_script",
        "screening_process",
        "inequality_context",
        "communication_training",
    }

    block_doc_types = {
        "personal_story",
        "meeting_notes",
        "roundtable_transcript",
    }

    chunk_token_min: int = 120
    chunk_token_max: int = 420

    top_k: int = 8
    max_context_tokens: int = 1200

    embedding_model: str = "text-embedding-3-large"
    chat_model: str = "gpt-4o-mini"
    embedding_batch_size: int = 96
