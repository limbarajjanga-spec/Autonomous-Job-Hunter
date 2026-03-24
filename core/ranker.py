# core/ranker.py
import os
os.environ["HF_HUB_DISABLE_IMPLICIT_TOKEN"] = "1"
import re
import numpy as np
from pathlib import Path
from loguru import logger
from sentence_transformers import SentenceTransformer
from pdfminer.high_level import extract_text
from core.config import load_profile
from core.deduper import is_duplicate, mark_seen

MODEL = SentenceTransformer("all-MiniLM-L6-v2")

def _load_resume_text() -> str:
    profile = load_profile()
    path    = Path(profile["resume_path"])

    # try PDF first
    if path.exists():
        try:
            text = extract_text(str(path))
            if text and len(text.strip()) > 100:
                logger.info(f"Resume loaded from PDF: {path}")
                return text
            else:
                logger.warning("PDF extracted but empty — trying .txt fallback")
        except Exception as e:
            logger.warning(f"PDF read failed ({e}) — trying .txt fallback")

    # fall back to .txt
    txt_path = path.with_suffix(".txt")
    if txt_path.exists():
        text = txt_path.read_text(encoding="utf-8")
        logger.info(f"Resume loaded from TXT: {txt_path}")
        return text

    # last resort — skills from profile
    logger.warning("No resume file found — using skills from profile.yaml")
    skills = profile["skills"]["core"] + profile["skills"].get("bonus", [])
    return " ".join(skills)



def _clean(text: str) -> str:
    return re.sub(r"\s+", " ", text.strip().lower())

# Load once at import time — avoids re-loading on every call
RESUME_TEXT      = _load_resume_text()
RESUME_EMBEDDING = MODEL.encode(_clean(RESUME_TEXT), normalize_embeddings=True)

def score_and_filter(jobs: list[dict]) -> list[dict]:
    """
    Scores each job against resume, removes duplicates, 
    returns only jobs above min_match_score — sorted best first.
    """
    profile   = load_profile()
    threshold = float(profile.get("min_match_score", 0.65))
    results   = []

    for job in jobs:
        # Build text to embed: title + company + description + tags
        jd_text = _clean(
            job["title"] + " " +
            job["company"] + " " +
            " ".join(job.get("tags", [])) + " " +
            job.get("description", "")[:800]
        )
        job_embedding = MODEL.encode(jd_text, normalize_embeddings=True)

        # Skip duplicates
        if is_duplicate(job, job_embedding):
            logger.debug(f"Duplicate skipped: {job['title']} @ {job['company']}")
            continue

        # Score against resume
        score = float(np.dot(RESUME_EMBEDDING, job_embedding))
        job["match_score"] = round(score, 4)

        # Only keep relevant jobs
        if score >= threshold:
            mark_seen(job, job_embedding)
            results.append(job)
        else:
            logger.debug(f"Low score {score:.2f} — skipped: {job['title']}")

    # Sort best match first
    results.sort(key=lambda j: j["match_score"], reverse=True)
    logger.success(f"Ranker: {len(results)} relevant jobs after filtering")
    return results