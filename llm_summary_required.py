import re
import unicodedata
from difflib import SequenceMatcher

def normalize(text: str) -> str:
    text = unicodedata.normalize("NFKD", text)
    text = text.lower()
    text = re.sub(r"\s+", " ", text)
    text = re.sub(r"[^\w\s]", "", text)
    return text.strip()


def similarity(a: str, b: str) -> float:
    return SequenceMatcher(None, a, b).ratio()

def needs_llm_summary(title: str, summary: str) -> bool:
    if not summary:
        return True

    title_n = normalize(title)
    summary_n = normalize(summary)

    # Remove trailing publisher words (last token heuristics)
    summary_n = summary_n.rsplit(" ", maxsplit=2)[0]

    sim = similarity(title_n, summary_n)

    # If summary is basically title → bad
    if sim > 0.85:
        return True

    # Too short to be meaningful
    if len(summary_n) < 40:
        return True

    return False
