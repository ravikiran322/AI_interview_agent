import sqlite3
from typing import Optional, Dict, Any, List
import time
import json


DB_PATH = "ai_interviews.db"


def init_db(path: str = DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("""
    CREATE TABLE IF NOT EXISTS interviews (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        role TEXT,
        persona TEXT,
        started_at REAL,
        ended_at REAL,
        total_score REAL
    )
    """)
    cur.execute("""
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        interview_id INTEGER,
        question TEXT,
        answer TEXT,
        score REAL,
        metadata TEXT,
        timestamp REAL
    )
    """)
    conn.commit()
    conn.close()


def save_interview(role: str, persona: str, total_score: float, path: str = DB_PATH) -> int:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    started = time.time()
    cur.execute("INSERT INTO interviews (role, persona, started_at, ended_at, total_score) VALUES (?,?,?,?,?)",
                (role, persona, started, time.time(), total_score))
    iid = cur.lastrowid
    conn.commit()
    conn.close()
    return iid


def save_answer(interview_id: int, question: str, answer: str, score: float, metadata: Dict = None, path: str = DB_PATH):
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("INSERT INTO answers (interview_id, question, answer, score, metadata, timestamp) VALUES (?,?,?,?,?,?)",
                (interview_id, question, answer, score, json.dumps(metadata or {}), time.time()))
    conn.commit()
    conn.close()


def list_interviews(path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT id, role, persona, started_at, ended_at, total_score FROM interviews ORDER BY id DESC")
    rows = cur.fetchall()
    conn.close()
    return [dict(id=r[0], role=r[1], persona=r[2], started_at=r[3], ended_at=r[4], total_score=r[5]) for r in rows]


def get_interview(interview_id: int, path: str = DB_PATH) -> Optional[Dict[str, Any]]:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT id, role, persona, started_at, ended_at, total_score FROM interviews WHERE id=?", (interview_id,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return dict(id=row[0], role=row[1], persona=row[2], started_at=row[3], ended_at=row[4], total_score=row[5])


def get_answers(interview_id: int, path: str = DB_PATH) -> List[Dict[str, Any]]:
    conn = sqlite3.connect(path)
    cur = conn.cursor()
    cur.execute("SELECT id, question, answer, score, metadata, timestamp FROM answers WHERE interview_id=? ORDER BY id", (interview_id,))
    rows = cur.fetchall()
    conn.close()
    out = []
    for r in rows:
        meta = {}
        try:
            meta = json.loads(r[4] or "{}")
        except Exception:
            meta = {}
        out.append({"id": r[0], "question": r[1], "answer": r[2], "score": r[3], "metadata": meta, "timestamp": r[5]})
    return out


def export_interviews_to_excel(path_out: str = "interviews_export.xlsx", db_path: str = DB_PATH) -> str:
    import pandas as pd
    ints = list_interviews(path=db_path)
    all_rows = []
    for it in ints:
        answers = get_answers(it["id"], path=db_path)
        if not answers:
            all_rows.append({"interview_id": it["id"], "role": it["role"], "persona": it["persona"], "question": None, "answer": None, "score": it.get("total_score", None)})
        for a in answers:
            all_rows.append({"interview_id": it["id"], "role": it["role"], "persona": it["persona"], "question": a["question"], "answer": a["answer"], "score": a["score"]})
    df = pd.DataFrame(all_rows)
    df.to_excel(path_out, index=False)
    return path_out
