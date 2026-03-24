# scrapers/remoteok.py
import requests
from loguru import logger
from scrapers.base import Job

REMOTEOK_URL = "https://remoteok.com/api"

TAGS_TO_MATCH = [
    "python", "machine learning", "ml", "ai", "llm", "nlp",
    "deep learning", "data science", "pytorch", "tensorflow",
    "langchain", "rag", "mlops", "huggingface", "generative"
]

def scrape(keywords: list[str]) -> list[Job]:
    jobs = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (job-hunter-bot/1.0)"}
        resp = requests.get(REMOTEOK_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        listings = [d for d in data if isinstance(d, dict) and "position" in d]

        for item in listings:
            title = item.get("position", "")
            tags  = [t.lower() for t in item.get("tags", [])]
            text  = (title + " " + " ".join(tags)).lower()

            if not any(t in text for t in TAGS_TO_MATCH):
                continue

            jobs.append(Job(
                title      = title,
                company    = item.get("company", "Unknown"),
                url        = item.get("url", f"https://remoteok.com/jobs/{item.get('id','')}"),
                source     = "RemoteOK",
                description= item.get("description", ""),
                location   = "Remote",
                salary     = item.get("salary", ""),
                tags       = item.get("tags", []),
                posted_at  = item.get("date", ""),
            ))

        logger.info(f"RemoteOK: {len(jobs)} matching jobs found")
    except Exception as e:
        logger.error(f"RemoteOK scraper failed: {e}")
    return jobs