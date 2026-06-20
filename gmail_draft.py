import os
import base64
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

TOKEN_PATH = os.getenv("GMAIL_TOKEN_PATH", "token.json")
CREDENTIALS_PATH = os.getenv("GMAIL_CREDENTIALS_PATH", "credentials.json")


def get_gmail_service():
    creds = None

    if os.path.exists(TOKEN_PATH):
        creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

    if not creds or not creds.valid:
        raise Exception(
            "Gmail token not found or invalid. On Render, add token.json as a Secret File."
        )

    return build("gmail", "v1", credentials=creds)


def create_draft(to, subject, body):
    service = get_gmail_service()

    message = EmailMessage()
    message.set_content(body)
    message["To"] = to
    message["Subject"] = subject

    encoded_message = base64.urlsafe_b64encode(
        message.as_bytes()
    ).decode()

    sent_message = service.users().messages().send(
        userId="me",
        body={"raw": encoded_message}
    ).execute()

    return f"Send successfully: {sent_message['id']}"


if __name__ == "__main__":
    create_draft(
        to="test@example.com",
        subject="Test Email from Python",
        body="Hello, this email was sent using Gmail API."
    )