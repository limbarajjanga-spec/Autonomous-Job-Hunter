# scrapers/remoteok.py
import requests
from loguru import logger
from scrapers.base import Job

REMOTEOK_URL = "https://remoteok.com/api"

def scrape(keywords: list[str]) -> list[Job]:
    jobs = []
    try:
        headers = {"User-Agent": "Mozilla/5.0 (job-hunter-bot/1.0)"}
        resp = requests.get(REMOTEOK_URL, headers=headers, timeout=15)
        resp.raise_for_status()
        data = resp.json()

        # First item is a legal notice dict, skip it
        listings = [d for d in data if isinstance(d, dict) and "position" in d]

        # smarter matching — any single word from any keyword matches
        kw_words = set()
        for k in keywords:
         kw_words.update(k.lower().split())
# remove generic words that match everything
        kw_words -= {"engineer", "remote", "senior", "junior"}

        for item in listings:
         title = item.get("position", "")
         tags  = item.get("tags", [])
         text  = (title + " " + " ".join(tags)).lower()

         if not any(w in text for w in kw_words):
             continue
             jobs.append(Job(
                title      = title,
                company    = item.get("company", "Unknown"),
                url        = item.get("url", f"https://remoteok.com/jobs/{item.get('id','')}"),
                source     = "RemoteOK",
                description= item.get("description", ""),
                location   = "Remote",
                salary     = item.get("salary", ""),
                tags       = tags,
                posted_at  = item.get("date", ""),
            ))

        logger.info(f"RemoteOK: {len(jobs)} matching jobs found")
    except Exception as e:
        logger.error(f"RemoteOK scraper failed: {e}")
    return jobs