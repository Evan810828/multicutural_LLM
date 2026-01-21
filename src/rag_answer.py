from typing import List, Dict, Any, Tuple

import tiktoken
from openai import OpenAI

from config import Settings
from prompts import SYSTEM_PROMPT, USER_TEMPLATE
from retrieve import Retriever


def _encoding():
    return tiktoken.get_encoding("cl100k_base")


def _count_tokens(text: str) -> int:
    return len(_encoding().encode(text))


def assemble_context(hits: List[Dict[str, Any]], max_tokens: int) -> str:
    seen = set()
    blocks = []
    total = 0

    for h in hits:
        key = (h.get("doc_id"), h.get("chunk_id"))
        if key in seen:
            continue
        seen.add(key)

        source = h.get("source_name", "Unknown")
        text = h.get("text", "")
        block = f"Source: {source}\n{text}"
        block_tokens = _count_tokens(block)

        if total + block_tokens > max_tokens:
            break

        blocks.append(block)
        total += block_tokens

    return "\n\n---\n\n".join(blocks)


def answer(question: str, use_rag: bool = True) -> Tuple[str, List[Dict[str, Any]]]:
    s = Settings()
    client = OpenAI()

    hits: List[Dict[str, Any]] = []
    if use_rag:
        hits = Retriever().retrieve(question, top_k=s.top_k)
        context = assemble_context(hits, max_tokens=s.max_context_tokens)
    else:
        context = "(no background found)"

    user_msg = USER_TEMPLATE.format(question=question, context=context or "(no background found)")

    res = client.chat.completions.create(
        model=s.chat_model,
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": user_msg},
        ],
        temperature=0.2,
    )

    return res.choices[0].message.content.strip(), hits


if __name__ == "__main__":
    q = "What happens during a mammogram?"
    response, _ = answer(q, use_rag=True)
    print(response)
