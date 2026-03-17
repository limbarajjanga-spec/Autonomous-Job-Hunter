# delivery/telegram_sender.py
import requests
from loguru import logger
from core.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHAT_ID
import json

TELEGRAM_API = "https://api.telegram.org/bot"

def send_message(text: str) -> bool:
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        logger.warning("Telegram not configured — skipping")
        return False
    try:
        url  = f"{TELEGRAM_API}{TELEGRAM_BOT_TOKEN}/sendMessage"
        resp = requests.post(url, json={
            "chat_id":    TELEGRAM_CHAT_ID,
            "text":       text,
            "parse_mode": "Markdown"
        }, timeout=10)
        resp.raise_for_status()
        logger.success("Telegram message sent")
        return True
    except Exception as e:
        logger.error(f"Telegram failed: {e}")
        return False

def send_digest(jobs: list[dict]) -> bool:
    if not jobs:
        return send_message("No new matching jobs found today.")

    lines = [f"*Your job digest — {len(jobs)} new matches*\n"]
    for job in jobs[:10]:
        score = int(job.get("match_score", 0) * 100)
        jd    = json.loads(job.get("jd_analysis", "{}"))
        sal   = jd.get("salary_range", "") or ""
        lines.append(
            f"*{job['title']}*\n"
            f"{job['company']} · {job.get('source','')}\n"
            f"Match: {score}%  |  {sal}\n"
            f"[Apply]({job['url']})\n"
        )

    return send_message("\n".join(lines))