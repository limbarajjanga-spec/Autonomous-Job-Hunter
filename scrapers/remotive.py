# scrapers/remotive.py
import requests
from loguru import logger
from scrapers.base import Job

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"

TAGS_TO_MATCH = [
    "python", "machine learning", "ml", "ai", "llm", "nlp",
    "deep learning", "data science", "pytorch", "tensorflow",
    "langchain", "rag", "mlops", "huggingface", "generative",
    "data engineer", "ai engineer", "ml engineer"
]

def scrape(keywords: list[str]) -> list[Job]:
    jobs = []
    try:
        resp = requests.get(REMOTIVE_URL, timeout=15)
        resp.raise_for_status()
        listings = resp.json().get("jobs", [])

        for item in listings:
            title    = item.get("title", "")
            tags     = [t.lower() for t in item.get("tags", [])]
            category = item.get("category", "").lower()
            desc     = item.get("description", "")[:300].lower()
            text     = (title + " " + " ".join(tags) + " " + category + " " + desc).lower()

            if not any(t in text for t in TAGS_TO_MATCH):
                continue

            jobs.append(Job(
                title      = title,
                company    = item.get("company_name", "Unknown"),
                url        = item.get("url", ""),
                source     = "Remotive",
                description= item.get("description", ""),
                location   = item.get("candidate_required_location", "Remote"),
                salary     = item.get("salary", ""),
                tags       = item.get("tags", []),
                posted_at  = item.get("publication_date", ""),
            ))

        logger.info(f"Remotive: {len(jobs)} matching jobs found")
    except Exception as e:
        logger.error(f"Remotive scraper failed: {e}")
    return jobs