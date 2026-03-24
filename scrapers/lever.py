# scrapers/lever.py
import requests
from loguru import logger
from scrapers.base import Job

COMPANIES = [
    "nvidia", "cerebras", "adept", "mosaic-ml",
    "modal-labs", "baseten", "lightning-ai",
    "determined-ai", "scale-ai", "hugging-face",
]

TAGS_TO_MATCH = [
    "machine learning", "ml", "ai", "llm", "nlp",
    "deep learning", "python", "engineer", "research"
]

def _fetch_company(company: str) -> list[Job]:
    jobs = []
    try:
        url  = f"https://api.lever.co/v0/postings/{company}?mode=json"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return []
        for item in resp.json():
            title = item.get("text", "")
            tags  = item.get("tags", [])
            text  = (title + " " + " ".join(tags)).lower()
            if not any(t in text for t in TAGS_TO_MATCH):
                continue
            jobs.append(Job(
                title   = title,
                company = company.replace("-", " ").title(),
                url     = item.get("hostedUrl", ""),
                source  = "Lever",
                location= item.get("categories", {}).get("location", "Remote"),
            ))
    except Exception:
        pass
    return jobs

def scrape(keywords: list[str]) -> list[Job]:
    jobs = []
    for company in COMPANIES:
        found = _fetch_company(company)
        jobs.extend(found)
        if found:
            logger.debug(f"Lever {company}: {len(found)} jobs")
    logger.info(f"Lever: {len(jobs)} matching jobs found")
    return jobs