import hashlib
import json
from pathlib import Path
from typing import Iterable

from docx import Document

from config import Settings
from privacy import is_personal


def read_docx(path: Path) -> str:
    d = Document(str(path))
    return "\n".join(p.text for p in d.paragraphs if p.text.strip())


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8", errors="ignore")


def infer_doc_type(path: Path) -> str:
    name = path.name.lower()
    if "story" in name or "luella" in name or "pam" in name:
        return "personal_story"
    if "screen" in name:
        return "screening_process"
    if "barrier" in name or "access" in name or "inequal" in name:
        return "inequality_context"
    if "module" in name or "script" in name or "training" in name:
        return "education_script"
    return "unknown"


def infer_module(path: Path) -> str:
    name = path.stem
    for token in name.replace("_", " ").split():
        if token.lower().startswith("module"):
            return " ".join(name.split()[:2])
    return "Unknown"


def iter_source_files(dirs: Iterable[Path]) -> Iterable[Path]:
    for root in dirs:
        if not root.exists():
            continue
        for p in root.rglob("*"):
            if p.is_dir():
                continue
            if p.suffix.lower() not in {".docx", ".txt"}:
                continue
            if "excluded" in p.parts or "processed" in p.parts or "index" in p.parts:
                continue
            yield p


def ingest() -> None:
    s = Settings()
    s.processed_dir.mkdir(parents=True, exist_ok=True)
    s.excluded_dir.mkdir(parents=True, exist_ok=True)

    raw_dirs = [s.raw_dir]
    if not any(s.raw_dir.rglob("*")):
        raw_dirs.append(s.project_root / "data")

    with s.docs_jsonl.open("w", encoding="utf-8") as out:
        for p in iter_source_files(raw_dirs):
            text = read_docx(p) if p.suffix.lower() == ".docx" else read_text(p)
            text = text.strip()
            if not text:
                continue

            doc_type = infer_doc_type(p)

            if doc_type in s.block_doc_types or is_personal(text):
                if s.raw_dir in p.parents:
                    target = s.excluded_dir / p.name
                    p.rename(target)
                continue

            rec = {
                "doc_id": hashlib.sha256(text.encode("utf-8")).hexdigest()[:16],
                "source_path": str(p),
                "source_name": p.stem,
                "doc_type": doc_type,
                "module": infer_module(p),
                "text": text,
            }
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    ingest()
