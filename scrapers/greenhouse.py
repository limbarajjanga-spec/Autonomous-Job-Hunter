# scrapers/greenhouse.py
import requests
from loguru import logger
from scrapers.base import Job

COMPANIES = [
    "anthropic", "cohere", "huggingface", "scaleai",
    "together", "replicate", "wandb", "modal",
    "mistral", "perplexity", "groq", "anyscale",
    "databricks", "deeplearning-ai", "synthesis",
    "imbue", "adept", "inflection",
    "stability", "runway",
]

TAGS_TO_MATCH = [
    "machine learning", "ml", "ai", "llm", "nlp",
    "deep learning", "data science", "python",
    "engineer", "research", "scientist"
]

def _fetch_company(company: str) -> list[Job]:
    jobs = []
    try:
        url  = f"https://boards-api.greenhouse.io/v1/boards/{company}/jobs"
        resp = requests.get(url, timeout=10)
        if resp.status_code != 200:
            return []
        for item in resp.json().get("jobs", []):
            title = item.get("title", "")
            text  = title.lower()
            if not any(t in text for t in TAGS_TO_MATCH):
                continue
            jobs.append(Job(
                title   = title,
                company = company.replace("-", " ").title(),
                url     = item.get("absolute_url", ""),
                source  = "Greenhouse",
                location= "Remote",
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
            logger.debug(f"Greenhouse {company}: {len(found)} jobs")
    logger.info(f"Greenhouse: {len(jobs)} matching jobs found")
    return jobs