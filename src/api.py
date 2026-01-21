from fastapi import FastAPI
from pydantic import BaseModel

from rag_answer import answer

app = FastAPI(title="Privacy-First RAG API")


class Question(BaseModel):
    question: str
    use_rag: bool = True


@app.post("/answer")
def answer_question(payload: Question):
    response, hits = answer(payload.question, use_rag=payload.use_rag)
    return {
        "answer": response,
        "hits": [
            {
                "chunk_id": h.get("chunk_id"),
                "source_name": h.get("source_name"),
                "score": h.get("score"),
            }
            for h in hits
        ],
    }
