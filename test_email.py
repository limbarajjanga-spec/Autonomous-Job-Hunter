# test_email.py
from delivery.digest       import get_todays_jobs, build_html_digest
from delivery.email_sender import send_digest
from datetime import datetime

jobs = get_todays_jobs()

if not jobs:
    print("No jobs in DB — running pipeline first...")
    from scrapers.runner import run_all_scrapers
    from core.pipeline   import process_jobs
    scraped = run_all_scrapers()
    results = process_jobs(scraped[:2])
    jobs    = get_todays_jobs()

date_str = datetime.now().strftime("%d %b %Y")
subject  = f"Job digest {date_str} — {len(jobs)} new matches"
html     = build_html_digest(jobs)

print(f"Sending digest with {len(jobs)} jobs...")
success = send_digest(subject, html)

if success:
    print("Email sent. Check your inbox at limbaraj.janga@gmail.com")
else:
    print("Email failed — check logs above.")