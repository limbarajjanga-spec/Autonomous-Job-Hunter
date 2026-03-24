# setup_gmail.py
from pathlib import Path
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES     = ["https://www.googleapis.com/auth/gmail.send"]
TOKEN_FILE = Path("config/gmail_token.json")
CREDS_FILE = Path("config/gmail_credentials.json")

def setup():
    if not CREDS_FILE.exists():
        print("ERROR: config/gmail_credentials.json not found.")
        print("Download it from Google Cloud Console and put it in config/")
        return

    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow  = InstalledAppFlow.from_client_secrets_file(
                str(CREDS_FILE), SCOPES
            )
            creds = flow.run_local_server(port=0)
        TOKEN_FILE.write_text(creds.to_json())
        print("Token saved to config/gmail_token.json")

    print("Gmail OAuth setup complete.")

if __name__ == "__main__":
    setup()