import os
import json
import math
import openai
from typing import Dict


def embed_text(text: str, api_key: str = None, model: str = None):
    if api_key:
        openai.api_key = api_key
    model = model or os.getenv("OPENAI_EMBED_MODEL", "text-embedding-3-small")
    try:
        resp = openai.Embedding.create(model=model, input=text)
        return resp["data"][0]["embedding"]
    except Exception:
        return None


def cosine(a, b):
    if not a or not b:
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    mag_a = math.sqrt(sum(x * x for x in a))
    mag_b = math.sqrt(sum(y * y for y in b))
    if mag_a == 0 or mag_b == 0:
        return 0.0
    return dot / (mag_a * mag_b)


def deep_evaluate(question: str, answer: str, ideal_answer: str = None, api_key: str = None) -> Dict:
    """Return a rich evaluation object with grammar, reasoning, explanation depth, behavioral traits, consistency.
    Uses embeddings to compare with ideal answer when available.
    """
    # Basic heuristics
    words = len(answer.split())
    grammar = max(0, min(100, 80 if words > 10 else 60))
    reasoning = 60
    explanation_depth = min(100, words)
    behavioral_traits = {"ownership": 50, "teamwork": 50, "leadership": 40}
    consistency = 80

    # If ideal answer provided and API available, compute semantic similarity
    try:
        if ideal_answer and api_key:
            emb_ans = embed_text(answer, api_key=api_key)
            emb_ideal = embed_text(ideal_answer, api_key=api_key)
            if emb_ans and emb_ideal:
                sim = cosine(emb_ans, emb_ideal)
                # map similarity to scores
                reasoning = min(100, int(sim * 100))
                explanation_depth = min(100, int((words / 200.0) * 100) + int(sim * 50))
                consistency = int(sim * 100)
    except Exception:
        pass

    return {
        "grammar_quality": grammar,
        "logical_reasoning": reasoning,
        "explanation_depth": explanation_depth,
        "behavioral_traits": behavioral_traits,
        "consistency": consistency,
    }
