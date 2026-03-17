# scrapers/runner.py
from concurrent.futures import ThreadPoolExecutor, as_completed
from loguru import logger
from core.config import load_profile
from core.ranker import score_and_filter
import scrapers.remoteok       as remoteok_scraper
import scrapers.weworkremotely as wwr_scraper
import scrapers.remotive       as remotive_scraper
import scrapers.linkedin       as linkedin_scraper

def run_all_scrapers() -> list[dict]:
    profile  = load_profile()
    keywords = profile["search_queries"]

    scrapers = {
        "RemoteOK":       lambda: remoteok_scraper.scrape(keywords),
        "WeWorkRemotely": lambda: wwr_scraper.scrape(keywords),
        "Remotive":       lambda: remotive_scraper.scrape(keywords),
        "LinkedIn":       lambda: linkedin_scraper.scrape(keywords),
    }

    all_jobs = []

    with ThreadPoolExecutor(max_workers=4) as pool:
        futures = {pool.submit(fn): name for name, fn in scrapers.items()}
        for future in as_completed(futures):
            name = futures[future]
            try:
                jobs = future.result()
                # convert Job objects → dicts here
                all_jobs.extend([j.to_dict() if hasattr(j, "to_dict") else j for j in jobs])
                logger.info(f"{name}: returned {len(jobs)} jobs")
            except Exception as e:
                logger.error(f"{name} failed: {e}")

    # Deduplicate by ID
    seen, unique = set(), []
    for job in all_jobs:
        if job["id"] not in seen:
            seen.add(job["id"])
            unique.append(job)

    logger.info(f"Raw unique jobs: {len(unique)}")

    # Score against resume + filter
    relevant = score_and_filter(unique)
    return relevant