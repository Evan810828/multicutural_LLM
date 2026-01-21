import re

TRIGGERS = [
    "i was diagnosed",
    "my chemo",
    "my surgery",
    "i had radiation",
    "my doctor",
    "i went to",
    "my cancer",
    "when i found out",
]


def is_personal(text: str) -> bool:
    t = text.lower()
    if any(k in t for k in TRIGGERS):
        return True
    if re.search(r"\b(19|20)\d{2}\b", t):
        return True
    if re.search(r"\bmy (mom|dad|sister|brother|aunt|uncle)\b", t):
        return True
    if re.search(r"\bi (was|am) (\d{1,2})\b", t):
        return True
    return False
