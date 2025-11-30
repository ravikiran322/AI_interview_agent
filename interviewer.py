import os
import random
from typing import List, Dict
from openai import OpenAI
from prompts import QUESTION_TEMPLATES, FOLLOWUP_PROMPT, SYSTEM_PROMPT
from evaluator import evaluate_answer


class Interviewer:
    def __init__(self, api_key: str = None, model: str = None):
        self.api_key = api_key or os.getenv("OPENAI_API_KEY")
        self.model = model or os.getenv("OPENAI_MODEL", "gpt-4o-mini")
        self.history: List[Dict] = []
        self.role = None
        self.in_progress = False
        self.queue: List[str] = []
        self.client = OpenAI(api_key=self.api_key)

    def start_interview(self, role: str):
        self.role = role
        self.in_progress = True
        self.history = []
        self.queue = self._build_question_queue(role)
        first_q = self._pop_next()
        self._append_system(first_q)

    def _append_system(self, text: str):
        self.history.append({"from": "system", "text": text})

    def _append_candidate(self, text: str):
        self.history.append({"from": "candidate", "text": text})

    def _build_question_queue(self, role: str) -> List[Dict]:
        bucket = QUESTION_TEMPLATES.get(role, {})
        qlist = []
        for t in ["technical", "behavioral", "situational"]:
            qlist.extend(bucket.get(t, []))
        random.shuffle(qlist)
        return qlist

    def _pop_next(self) -> str:
        return self.queue.pop(0)["q"] if self.queue else "Thank you. No more questions."

    def receive_answer(self, answer: str) -> Dict:
        # Append candidate answer
        self._append_candidate(answer)

        # Evaluate the answer
        eval_result = evaluate_answer(question=self.history[-2]["text"] if len(self.history) >= 2 else "",
                                      answer=answer,
                                      role=self.role or "",
                                      api_key=self.api_key,
                                      model=self.model)

        # Generate follow-up using LLM
        follow_up = self._generate_followup(self.history[-2]["text"] if len(self.history) >= 2 else "", answer)

        # Append follow up as next system question or next main question
        if follow_up:
            self._append_system(follow_up)
        else:
            if self.queue:
                self._append_system(self._pop_next())
            else:
                self._append_system("Interview complete. Press 'End Interview' to see the report.")

        return {"score": eval_result.get("score", 0), "breakdown": eval_result.get("breakdown", {}),
                "strengths": eval_result.get("strengths", []), "weaknesses": eval_result.get("weaknesses", []),
                "recommendation": eval_result.get("recommendation", "Consider")}

    def _generate_followup(self, question: str, answer: str) -> str:
        if not self.api_key:
            return ""
        prompt = FOLLOWUP_PROMPT.format(question=question, answer=answer, role=self.role)
        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "system", "content": SYSTEM_PROMPT}, {"role": "user", "content": prompt}],
                temperature=0.3,
                max_tokens=100,
            )
            follow = resp.choices[0].message.content.strip()
            # If the follow-up is empty or too similar to question, skip
            if not follow or len(follow) < 10:
                return ""
            return follow
        except Exception:
            return ""

    def end_interview(self) -> Dict:
        # Summarize results and provide final report
        # Aggregate evaluations from history: for simplicity, call evaluate on each candidate response
        candidate_answers = [h for h in self.history if h["from"] == "candidate"]
        total = 0.0
        breakdown_acc = {"relevance": 0.0, "technical_depth": 0.0, "clarity": 0.0, "structure": 0.0}
        items = []
        for idx, ca in enumerate(candidate_answers):
            q = self.history[2*idx]["text"] if 2*idx < len(self.history) else ""
            res = evaluate_answer(question=q, answer=ca["text"], role=self.role or "", api_key=self.api_key, model=self.model)
            score = res.get("score", 0.0)
            total += score
            bd = res.get("breakdown", {})
            for k in breakdown_acc:
                # handle naming differences
                breakdown_acc[k] += bd.get(k, bd.get(k.replace('technical_depth','technical_depth'), 0))
            items.append({"question": q, "answer": ca["text"], "evaluation": res})

        count = max(1, len(candidate_answers))
        avg = total / count
        # Normalize breakdown_avg
        breakdown_avg = {k: (v / count) for k, v in breakdown_acc.items()}

        # Determine recommendation based on avg
        if avg >= 75:
            decision = "Hire"
        elif avg >= 50:
            decision = "Consider"
        else:
            decision = "Reject"

        report = {
            "role": self.role,
            "total_score": avg,
            "breakdown_avg": breakdown_avg,
            "decision": decision,
            "items": items,
        }

        self.in_progress = False
        return report
