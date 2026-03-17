# core/deduper.py
import sqlite3
import numpy as np
from loguru import logger
from db.database import get_conn

def _cosine(a: np.ndarray, b: np.ndarray) -> float:
    denom = np.linalg.norm(a) * np.linalg.norm(b)
    return float(np.dot(a, b) / denom) if denom else 0.0

def is_duplicate(job: dict, embedding: np.ndarray, threshold=0.92) -> bool:
    """Returns True if a near-identical job already exists in seen_jobs."""
    conn = get_conn()
    rows = conn.execute("SELECT embedding FROM seen_jobs").fetchall()
    conn.close()

    for row in rows:
        stored = np.frombuffer(row[0], dtype=np.float32)
        if _cosine(embedding, stored) >= threshold:
            return True
    return False

def mark_seen(job: dict, embedding: np.ndarray):
    """Save job + its embedding so future runs skip it."""
    conn = get_conn()
    conn.execute(
        "INSERT OR IGNORE INTO seen_jobs (id, title, company, url, source, embedding) VALUES (?,?,?,?,?,?)",
        (job["id"], job["title"], job["company"],
         job["url"], job["source"], embedding.astype(np.float32).tobytes())
    )
    conn.commit()
    conn.close()