# scheduler.py
from apscheduler.schedulers.blocking import BlockingScheduler
from loguru import logger
from datetime import datetime

scheduler = BlockingScheduler(timezone="Asia/Kolkata")

@scheduler.scheduled_job("cron", hour=7, minute=0)
def daily_hunt():
    logger.info(f"Daily hunt started at {datetime.now()}")
    try:
        from scrapers.runner import run_all_scrapers
        from core.pipeline   import process_jobs
        from delivery.sender import deliver_all

        jobs    = run_all_scrapers()
        results = process_jobs(jobs)
        deliver_all()
        logger.success(f"Daily hunt complete — {len(results)} jobs processed")
    except Exception as e:
        logger.error(f"Daily hunt failed: {e}")

if __name__ == "__main__":
    logger.info("Scheduler started — runs daily at 7:00 AM IST")
    logger.info("Press Ctrl+C to stop")
    scheduler.start()