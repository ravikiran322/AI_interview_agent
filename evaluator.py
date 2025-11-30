import os
import json
from typing import Dict
from openai import OpenAI
from prompts import EVALUATION_PROMPT


def _ensure_key(api_key: str):
    if not api_key:
        raise ValueError("OpenAI API key is required. Set OPENAI_API_KEY env var or pass api_key.")


def evaluate_answer(question: str, answer: str, role: str, api_key: str, model: str = None) -> Dict:
    """Call the LLM to evaluate the answer and return structured evaluation data.

    Returns dict:
      - score (float)
      - breakdown (dict)
      - strengths (list)
      - weaknesses (list)
      - recommendation (str)
    """
    _ensure_key(api_key)
    client = OpenAI(api_key=api_key)
    model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")

    system = EVALUATION_PROMPT
    prompt = system.replace("{{question}}", question).replace("{{answer}}", answer).replace("{{role}}", role)

    try:
        resp = client.chat.completions.create(
            model=model,
            messages=[{"role": "system", "content": "You are a helpful evaluator."},
                      {"role": "user", "content": prompt}],
            temperature=0.2,
            max_tokens=600,
        )
        text = resp.choices[0].message.content.strip()
        # Try to parse JSON from the response
        data = json.loads(text)
        # Normalize some fields
        if "score" in data:
            data["score"] = float(data["score"])
        return data
    except Exception:
        # Fallback: perform simple heuristic scoring locally if LLM fails
        relevance = 20 if len(answer.split()) > 10 else 10
        technical = 20 if any(k in answer.lower() for k in ["design", "optimize", "sql", "api", "model"]) else 12
        clarity = 20 if len(answer.split('.')) > 1 else 12
        structure = 20 if any(word in answer.lower() for word in ["situation", "task", "action", "result"]) else 10
        total = relevance + technical + clarity + structure
        rec = "Consider" if total > 50 else "Reject"
        return {
            "score": float(total),
            "breakdown": {"relevance": relevance, "technical_depth": technical, "clarity": clarity, "structure": structure},
            "strengths": ["Provided some technical terms"],
            "weaknesses": ["Needs clearer structure and more depth"],
            "recommendation": rec,
        }
