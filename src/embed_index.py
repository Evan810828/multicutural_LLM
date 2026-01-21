import json
from typing import List

import faiss
import numpy as np
import pandas as pd
from openai import OpenAI

from config import Settings


def _batch(iterable: List[str], size: int):
    for i in range(0, len(iterable), size):
        yield iterable[i : i + size]


def build_index() -> None:
    s = Settings()
    s.index_dir.mkdir(parents=True, exist_ok=True)

    texts = []
    meta = []
    with s.chunks_jsonl.open("r", encoding="utf-8") as f:
        for line in f:
            rec = json.loads(line)
            texts.append(rec["text"])
            meta.append(rec)

    if not texts:
        raise RuntimeError("No chunks found. Run src/chunking.py first.")

    client = OpenAI()
    embeddings = []

    for batch in _batch(texts, s.embedding_batch_size):
        res = client.embeddings.create(model=s.embedding_model, input=batch)
        embeddings.extend([r.embedding for r in res.data])

    X = np.array(embeddings, dtype="float32")
    faiss.normalize_L2(X)

    index = faiss.IndexFlatIP(X.shape[1])
    index.add(X)

    faiss.write_index(index, str(s.faiss_index_path))
    pd.DataFrame(meta).to_parquet(s.meta_path, index=False)


if __name__ == "__main__":
    build_index()
