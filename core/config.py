# core/config.py
import os
import yaml
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

ROOT = Path(__file__).parent.parent

def load_profile() -> dict:
    with open(ROOT / "config" / "profile.yaml") as f:
        return yaml.safe_load(f)

# API keys — accessed throughout the project
ANTHROPIC_API_KEY   = os.getenv("ANTHROPIC_API_KEY")
GMAIL_SENDER        = os.getenv("GMAIL_SENDER")
GMAIL_RECIPIENT     = os.getenv("GMAIL_RECIPIENT")
TELEGRAM_BOT_TOKEN  = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID    = os.getenv("TELEGRAM_CHAT_ID")
TWILIO_SID          = os.getenv("TWILIO_ACCOUNT_SID")
TWILIO_TOKEN        = os.getenv("TWILIO_AUTH_TOKEN")
TWILIO_WA_FROM      = os.getenv("TWILIO_WHATSAPP_FROM")
SERPAPI_KEY         = os.getenv("SERPAPI_KEY")