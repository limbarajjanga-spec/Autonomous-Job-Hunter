# scrapers/linkedin.py
import requests
from bs4 import BeautifulSoup
from loguru import logger
from scrapers.base import Job
import time, random

BASE = "https://www.linkedin.com/jobs-guest/jobs/api/seeMoreJobPostings/search"

def scrape(keywords: list[str]) -> list[Job]:
    jobs = []
    query = " OR ".join(keywords[:3])   # LinkedIn handles OR queries

    params = {
        "keywords":  query,
        "location":  "Worldwide",
        "f_WT":      "2",          # Remote filter
        "start":     "0",
    }
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                      "AppleWebKit/537.36 (KHTML, like Gecko) "
                      "Chrome/120.0.0.0 Safari/537.36"
    }

    try:
        for start in [0, 25, 50]:          # 3 pages = ~75 jobs
            params["start"] = str(start)
            resp = requests.get(BASE, params=params, headers=headers, timeout=15)
            if resp.status_code != 200:
                logger.warning(f"LinkedIn returned {resp.status_code}")
                break

            soup = BeautifulSoup(resp.text, "html.parser")
            cards = soup.find_all("div", class_="base-card")

            if not cards:
                break

            for card in cards:
                title_el   = card.find("h3", class_="base-search-card__title")
                company_el = card.find("h4", class_="base-search-card__subtitle")
                link_el    = card.find("a", class_="base-card__full-link")

                if not title_el:
                    continue

                jobs.append(Job(
                    title   = title_el.get_text(strip=True),
                    company = company_el.get_text(strip=True) if company_el else "Unknown",
                    url     = link_el["href"].split("?")[0] if link_el else "",
                    source  = "LinkedIn",
                    location= "Remote",
                ))

            time.sleep(random.uniform(2, 4))   # be polite

        logger.info(f"LinkedIn: {len(jobs)} jobs found")
    except Exception as e:
        logger.error(f"LinkedIn scraper failed: {e}")
    return jobs