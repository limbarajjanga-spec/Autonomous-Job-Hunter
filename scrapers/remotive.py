# scrapers/remotive.py
import requests
from loguru import logger
from scrapers.base import Job

REMOTIVE_URL = "https://remotive.com/api/remote-jobs"

def scrape(keywords: list[str]) -> list[Job]:
    jobs = []

    # smarter matching — any single word from any keyword matches
    kw_words = set()
    for k in keywords:
        kw_words.update(k.lower().split())
    kw_words -= {"engineer", "remote", "senior", "junior"}

    try:
        resp = requests.get(REMOTIVE_URL, timeout=15)
        resp.raise_for_status()
        listings = resp.json().get("jobs", [])

        for item in listings:
            title = item.get("title", "")
            desc  = item.get("description", "")
            tags  = item.get("tags", [])
            text  = (title + " " + " ".join(tags) + " " + desc[:300]).lower()

            if not any(w in text for w in kw_words):
                continue

            jobs.append(Job(
                title      = title,
                company    = item.get("company_name", "Unknown"),
                url        = item.get("url", ""),
                source     = "Remotive",
                description= desc,
                location   = item.get("candidate_required_location", "Remote"),
                salary     = item.get("salary", ""),
                tags       = tags,
                posted_at  = item.get("publication_date", ""),
            ))

        logger.info(f"Remotive: {len(jobs)} matching jobs found")
    except Exception as e:
        logger.error(f"Remotive scraper failed: {e}")
    return jobs