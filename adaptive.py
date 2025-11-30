from typing import Dict, List

def compute_confidence_score(answer: str, evaluator_breakdown: Dict) -> float:
    # Simple heuristic: longer answers with good clarity/technical score => higher confidence
    length_score = min(len(answer.split()) / 50.0, 1.0) * 20
    clarity = evaluator_breakdown.get("clarity", 12)
    technical = evaluator_breakdown.get("technical_depth", 12)
    conf = (length_score * 0.3) + (clarity * 0.35) + (technical * 0.35)
    return max(0.0, min(100.0, conf))


def pick_next_question(role_templates: Dict, asked: List[str], difficulty: str, metrics: Dict) -> Dict:
    """Select next question adaptively. metrics contains keys like confidence, missed_topics (list), last_difficulty"""
    pool = []
    for section in role_templates.values():
        for item in section:
            # item may be dict with 'q'
            qtext = item["q"] if isinstance(item, dict) else item
            d = item.get("difficulty", "Intermediate") if isinstance(item, dict) else "Intermediate"
            pool.append({"q": qtext, "difficulty": d, "ideal": item.get("ideal") if isinstance(item, dict) else None})

    # Filter by difficulty preference and avoid repeats
    filtered = [p for p in pool if p["q"] not in asked]
    # If candidate weak/confidence low, pick simpler questions
    conf = metrics.get("confidence", 60)
    if conf < 40:
        candidates = [p for p in filtered if p["difficulty"] == "Beginner"]
    elif conf < 70:
        candidates = [p for p in filtered if p["difficulty"] in ("Beginner", "Intermediate")]
    else:
        candidates = [p for p in filtered if p["difficulty"] in ("Intermediate", "Expert")]

    # If missed_topics provided, prefer questions that touch them
    missed = set(metrics.get("missed_topics", []))
    for p in candidates:
        if p["ideal"]:
            for m in missed:
                if m.lower() in p["ideal"].lower():
                    return p

    if candidates:
        return candidates[0]
    # fallback
    return filtered[0] if filtered else {"q": "No more questions", "difficulty": "Beginner"}
