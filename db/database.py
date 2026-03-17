# db/database.py
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent / "jobs.db"

def get_conn():
    return sqlite3.connect(DB_PATH)

def init_db():
    conn = get_conn()
    conn.executescript("""
        CREATE TABLE IF NOT EXISTS seen_jobs (
            id          TEXT PRIMARY KEY,
            title       TEXT,
            company     TEXT,
            url         TEXT,
            source      TEXT,
            embedding   BLOB,
            seen_at     TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );

        CREATE TABLE IF NOT EXISTS processed_jobs (
            id              TEXT PRIMARY KEY,
            title           TEXT,
            company         TEXT,
            url             TEXT,
            source          TEXT,
            location        TEXT,
            salary          TEXT,
            match_score     REAL,
            jd_analysis     TEXT,
            tailored_resume TEXT,
            cover_letter    TEXT,
            interview_qa    TEXT,
            status          TEXT DEFAULT 'new',
            created_at      TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        );
    """)
    conn.commit()
    conn.close()
    print("DB initialized.")

if __name__ == "__main__":
    init_db()