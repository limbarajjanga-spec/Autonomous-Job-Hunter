# reset_and_run.py
import os
import shutil
from pathlib import Path

# ── clean pycache ──────────────────────────────────────────
for p in Path(".").rglob("__pycache__"):
    shutil.rmtree(p)
for p in Path(".").rglob("*.pyc"):
    p.unlink()
print("Cache cleared.")

# ── reset DB ───────────────────────────────────────────────
from db.database import init_db
db_path = Path("db/jobs.db")
if db_path.exists():
    db_path.unlink()
    print("Old DB deleted.")
init_db()

# ── scrape + rank ──────────────────────────────────────────
from scrapers.runner import run_all_scrapers
jobs = run_all_scrapers()
print(f"\nScraped {len(jobs)} relevant jobs")

if not jobs:
    print("No jobs found — delivery skipped.")
else:
    # ── pipeline: top 2 only (saves API tokens during testing) ──
    from core.pipeline import process_jobs
    results = process_jobs(jobs[:2])
    print(f"\nProcessed {len(results)} jobs through Claude agents")

    # ── deliver ────────────────────────────────────────────
    from delivery.sender import deliver_all
    deliver_all()
    print("\nDone. Check Telegram / email.")