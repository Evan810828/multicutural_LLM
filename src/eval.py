import json
from datetime import datetime

from config import Settings
from rag_answer import answer

QUESTIONS = [
    "What happens during a mammogram?",
    "I have no symptoms. Do I still need screening?",
    "When should I start screening?",
]


def run_eval() -> None:
    s = Settings()
    s.results_dir.mkdir(parents=True, exist_ok=True)
    out_path = s.results_dir / "eval.jsonl"

    with out_path.open("w", encoding="utf-8") as out:
        for q in QUESTIONS:
            rag_resp, rag_hits = answer(q, use_rag=True)
            static_resp, _ = answer(q, use_rag=False)

            rec = {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "question": q,
                "rag_response": rag_resp,
                "static_response": static_resp,
                "rag_hits": [
                    {
                        "chunk_id": h.get("chunk_id"),
                        "source_name": h.get("source_name"),
                        "score": h.get("score"),
                    }
                    for h in rag_hits
                ],
            }
            out.write(json.dumps(rec, ensure_ascii=False) + "\n")


if __name__ == "__main__":
    run_eval()
