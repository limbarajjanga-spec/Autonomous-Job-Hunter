# scrapers/weworkremotely.py
import feedparser
from loguru import logger
from scrapers.base import Job

FEEDS = [
    "https://weworkremotely.com/categories/remote-programming-jobs.rss",
    "https://weworkremotely.com/categories/remote-devops-sysadmin-jobs.rss",
    "https://weworkremotely.com/categories/remote-data-science-jobs.rss",
]

def scrape(keywords: list[str]) -> list[Job]:
    jobs = []
    kw_lower = [k.lower() for k in keywords]

    for feed_url in FEEDS:
        try:
            feed = feedparser.parse(feed_url)
            for entry in feed.entries:
                title   = entry.get("title", "")
                summary = entry.get("summary", "")
                text    = (title + " " + summary).lower()

                if not any(k in text for k in kw_lower):
                    continue

                # WWR title format: "Company: Job Title"
                parts   = title.split(":", 1)
                company = parts[0].strip() if len(parts) > 1 else "Unknown"
                role    = parts[1].strip() if len(parts) > 1 else title

                jobs.append(Job(
                    title      = role,
                    company    = company,
                    url        = entry.get("link", ""),
                    source     = "WeWorkRemotely",
                    description= summary,
                    location   = "Remote",
                    posted_at  = entry.get("published", ""),
                ))
        except Exception as e:
            logger.error(f"WWR feed {feed_url} failed: {e}")

    logger.info(f"WeWorkRemotely: {len(jobs)} matching jobs found")
    return jobs