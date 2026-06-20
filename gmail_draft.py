import os.path
import base64
from email.message import EmailMessage

from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ["https://www.googleapis.com/auth/gmail.send"]

def get_gmail_service():
    creds = None

    if os.path.exists("token.json"):
        creds = Credentials.from_authorized_user_file("token.json", SCOPES)

    if not creds or not creds.valid:
        flow = InstalledAppFlow.from_client_secrets_file(
            "credentials.json",
            SCOPES
        )
        creds = flow.run_local_server(port=0)

        with open("token.json", "w") as token:
            token.write(creds.to_json())

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

    draft = {
        "message": {
            "raw": encoded_message
        }
    }

    created_draft = service.users().messages().send(
        userId="me",
        body={
            "raw": encoded_message
        }
    ).execute()

    print("Send successfully:", created_draft["id"])

create_draft(
    to="test@example.com",
    subject="Test Draft from Python",
    body="Hello, this draft was created using Gmail API."
)