# delivery/whatsapp_sender.py
import os
from loguru import logger
from core.config import TWILIO_SID, TWILIO_TOKEN, TWILIO_WA_FROM
import json

WHATSAPP_TO = os.getenv("WHATSAPP_TO", "")

def send_digest(jobs: list[dict]) -> bool:
    if not TWILIO_SID or not TWILIO_TOKEN:
        logger.warning("Twilio not configured — skipping WhatsApp")
        return False
    if not WHATSAPP_TO:
        logger.warning("WHATSAPP_TO not set in .env — skipping WhatsApp")
        return False
    try:
        from twilio.rest import Client
        client = Client(TWILIO_SID, TWILIO_TOKEN)

        if not jobs:
            body = "No new matching jobs today."
        else:
            lines = [f"Job digest — {len(jobs)} new matches\n"]
            for job in jobs[:5]:
                score = int(job.get("match_score", 0) * 100)
                lines.append(
                    f"{job['title']} @ {job['company']}\n"
                    f"Match: {score}%\n"
                    f"{job['url']}\n"
                )
            body = "\n".join(lines)

        client.messages.create(
            from_=TWILIO_WA_FROM,
            to   =WHATSAPP_TO,
            body =body
        )
        logger.success("WhatsApp message sent")
        return True
    except Exception as e:
        logger.error(f"WhatsApp failed: {e}")
        return False