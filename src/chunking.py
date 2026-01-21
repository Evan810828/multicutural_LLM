import json
from typing import Iterable, List

import tiktoken

from config import Settings
from privacy import is_personal


def _encoding():
    return tiktoken.get_encoding("cl100k_base")


def count_tokens(text: str) -> int:
    enc = _encoding()
    return len(enc.encode(text))


def chunk_paragraphs(paragraphs: List[str], max_tokens: int) -> Iterable[str]:
    enc = _encoding()
    buf: List[str] = []
    buf_tokens = 0

    for p in paragraphs:
        p_tokens = len(enc.encode(p))
        if buf_tokens + p_tokens > max_tokens and buf:
            yield "\n".join(buf)
            buf = [p]
            buf_tokens = p_tokens
        else:
            buf.append(p)
            buf_tokens += p_tokens

    if buf:
        yield "\n".join(buf)


def chunk_docs() -> None:
    s = Settings()
    s.processed_dir.mkdir(parents=True, exist_ok=True)

    with s.docs_jsonl.open("r", encoding="utf-8") as src, s.chunks_jsonl.open(
        "w", encoding="utf-8"
    ) as out:
        for line in src:
            doc = json.loads(line)
            if doc.get("doc_type") not in s.allow_doc_types:
                continue

            text = doc.get("text", "")
            paragraphs = [p.strip() for p in text.split("\n") if p.strip()]

            for idx, chunk in enumerate(
                chunk_paragraphs(paragraphs, max_tokens=s.chunk_token_max)
            ):
                if is_personal(chunk):
                    continue
                n_tokens = count_tokens(chunk)
                if n_tokens < s.chunk_token_min:
                    continue

                rec = {
                    "chunk_id": f"{doc['doc_id']}_{idx}",
                    "doc_id": doc["doc_id"],
                    "source_path": doc["source_path"],
                    "source_name": doc["source_name"],
                    "module": doc["module"],
                    "doc_type": doc["doc_type"],
                    "text": chunk,
                    "n_tokens": n_tokens,
                }
                out.write(json.dumps(rec, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    chunk_docs()
