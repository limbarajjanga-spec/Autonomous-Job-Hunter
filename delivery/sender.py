# delivery/sender.py
from datetime import datetime
from loguru import logger
from delivery.digest          import build_html_digest, get_todays_jobs
from delivery.email_sender    import send_digest as send_email
from delivery.telegram_sender import send_digest as send_telegram
from delivery.whatsapp_sender import send_digest as send_whatsapp

def deliver_all():
    jobs     = get_todays_jobs()
    date_str = datetime.now().strftime("%d %b %Y")

    if not jobs:
        logger.warning("No new jobs to deliver today")
        send_telegram([])
        send_whatsapp([])
        return

    logger.info(f"Delivering digest — {len(jobs)} jobs")

    # Email
    html    = build_html_digest(jobs)
    subject = f"Job digest {date_str} — {len(jobs)} new matches"
    send_email(subject, html)

    # Telegram
    send_telegram(jobs)

    # WhatsApp
    send_whatsapp(jobs)

    logger.success("All delivery channels done")