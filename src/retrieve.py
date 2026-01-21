from typing import List, Dict, Any

import faiss
import numpy as np
import pandas as pd
from openai import OpenAI

from config import Settings


class Retriever:
    def __init__(self) -> None:
        self.s = Settings()
        self.client = OpenAI()
        self.index = faiss.read_index(str(self.s.faiss_index_path))
        self.meta = pd.read_parquet(self.s.meta_path)

    def embed_query(self, query: str) -> np.ndarray:
        res = self.client.embeddings.create(model=self.s.embedding_model, input=[query])
        vec = np.array(res.data[0].embedding, dtype="float32")
        faiss.normalize_L2(vec.reshape(1, -1))
        return vec.reshape(1, -1)

    def retrieve(self, query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
        k = top_k or self.s.top_k
        q = self.embed_query(query)
        scores, idxs = self.index.search(q, k)
        results = []
        for score, idx in zip(scores[0], idxs[0]):
            if idx < 0:
                continue
            row = self.meta.iloc[int(idx)].to_dict()
            row["score"] = float(score)
            results.append(row)
        return results


def retrieve(query: str, top_k: int | None = None) -> List[Dict[str, Any]]:
    return Retriever().retrieve(query, top_k=top_k)
