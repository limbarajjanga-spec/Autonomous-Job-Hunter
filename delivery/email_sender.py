# delivery/email_sender.py
import base64
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from pathlib import Path
from loguru import logger
from core.config import GMAIL_SENDER, GMAIL_RECIPIENT

SCOPES      = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_FILE  = Path("config/gmail_token.json")
CREDS_FILE  = Path("config/gmail_credentials.json")

def _get_service():
    creds = None
    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(str(CREDS_FILE), SCOPES)
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
    return build("gmail", "v1", credentials=creds)

def send_digest(subject: str, html_body: str) -> bool:
    if not CREDS_FILE.exists():
        logger.warning("Gmail credentials not set up — skipping email")
        return False
    try:
        service = _get_service()
        msg     = MIMEMultipart("alternative")
        msg["Subject"] = subject
        msg["From"]    = GMAIL_SENDER
        msg["To"]      = GMAIL_RECIPIENT
        msg.attach(MIMEText(html_body, "html"))

        raw = base64.urlsafe_b64encode(msg.as_bytes()).decode()
        service.users().messages().send(
            userId="me", body={"raw": raw}
        ).execute()
        logger.success(f"Email sent to {GMAIL_RECIPIENT}")
        return True
    except Exception as e:
        logger.error(f"Email failed: {e}")
        return False