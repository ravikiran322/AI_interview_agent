SYSTEM_PROMPT = """
You are an AI interview assistant used by enterprise hiring teams.
Always avoid hallucinations. Be factual, role-specific, and require multi-step reasoning for technical prompts.
When evaluating, use objective rubrics and the STAR method for structure.
Return structured JSON for evaluations when requested.
"""

# Questions are tagged with a difficulty level and an optional ideal answer or keywords for embedding-based comparison.
QUESTION_TEMPLATES = {
    "Software Engineer": {
        "technical": [
            {"q": "Explain the difference between process and thread.", "difficulty": "Beginner", "ideal": "process isolation, memory, context switch cost, concurrency vs parallelism"},
            {"q": "Design a scalable URL shortener (high level).", "difficulty": "Intermediate", "ideal": "hashing, collisions, datastore, caching, short id generation, scaling, analytics"},
            {"q": "How would you optimize a slow SQL query?", "difficulty": "Expert", "ideal": "indexes, explain plan, denormalization, query rewrite, caching, partitioning"},
        ],
        "behavioral": [
            {"q": "Tell me about a time you had to debug a hard production issue.", "difficulty": "Intermediate", "ideal": "monitoring, rollback, RCA, communication"},
            {"q": "Describe a situation where you disagreed with a teammate.", "difficulty": "Beginner", "ideal": "communication, compromise, data-driven"},
        ],
        "situational": [
            {"q": "How would you approach estimating time for a complex feature?", "difficulty": "Intermediate", "ideal": "breakdown, assumptions, buffers, dependencies"},
        ],
    },
    "Data Scientist": {
        "technical": [
            {"q": "Explain bias-variance tradeoff.", "difficulty": "Beginner", "ideal": "underfitting vs overfitting, validation, regularization"},
            {"q": "How do you validate a predictive model for production?", "difficulty": "Expert", "ideal": "metrics, monitoring, drift detection, A/B tests"},
        ],
        "behavioral": [
            {"q": "Describe a time you turned messy data into insights.", "difficulty": "Intermediate", "ideal": "cleaning, feature engineering, impact"},
        ],
        "situational": [
            {"q": "How would you prioritize features for a machine learning pipeline?", "difficulty": "Intermediate", "ideal": "business impact, data availability, effort"},
        ],
    },
    "DevOps Engineer": {
        "technical": [
            {"q": "Explain how you would design CI/CD for a microservices app.", "difficulty": "Intermediate", "ideal": "pipelines, canary, blue-green, infra-as-code, observability"},
        ],
        "behavioral": [
            {"q": "Tell me about a time you reduced deployment downtime.", "difficulty": "Intermediate", "ideal": "automation, rollback, monitoring"},
        ],
        "situational": [
            {"q": "How would you respond to repeated flaky deployments?", "difficulty": "Expert", "ideal": "root cause, stabilization, test flakiness"},
        ],
    },
    "Product Manager": {
        "technical": [
            {"q": "How do you perform prioritization between competing features?", "difficulty": "Intermediate", "ideal": "RICE, impact vs effort, stakeholder alignment"},
        ],
        "behavioral": [
            {"q": "Describe a time you handled stakeholder conflict.", "difficulty": "Beginner", "ideal": "listening, data, compromise"},
        ],
        "situational": [
            {"q": "How would you scope an MVP for a new product?", "difficulty": "Intermediate", "ideal": "core value, user journeys, metrics"},
        ],
    },
    "Frontend Engineer": {
        "technical": [
            {"q": "Explain how the virtual DOM works.", "difficulty": "Beginner", "ideal": "diffing, reconciliation, render optimization"},
            {"q": "How do you approach performance optimization in web apps?", "difficulty": "Expert", "ideal": "lazy loading, critical rendering path, caching, bundle size"},
        ],
        "behavioral": [
            {"q": "Tell me about a time you improved frontend accessibility.", "difficulty": "Intermediate", "ideal": "a11y standards, ARIA, testing"},
        ],
        "situational": [
            {"q": "How would you migrate a legacy UI to a modern framework?", "difficulty": "Intermediate", "ideal": "incremental migration, adapters, tests"},
        ],
    },
}

EVALUATION_PROMPT = """
You are an expert interviewer and evaluator. Given the question, candidate answer, and role, provide a JSON object with:
 - score: 0-100 overall
 - breakdown: object with relevance, technical_depth, clarity, structure (each 0-25)
 - strengths: array of brief strengths
 - weaknesses: array of brief weaknesses
 - recommendation: one of ["Hire", "Consider", "Reject"]

Provide only valid JSON in the response.
Here are the fields you will receive:
{{question}}
{{answer}}
{{role}}
Use the STAR method in structure evaluation: Situation, Task, Action, Result.
"""

FOLLOWUP_PROMPT = """
You are an AI interviewer. The candidate just answered the question below. Generate one concise follow-up question that digs deeper into technical details or clarifies parts of their answer. If the answer is incomplete, ask for a more structured explanation. Return only the follow-up question as plain text.

Question: {question}
Answer: {answer}
Role: {role}
"""
