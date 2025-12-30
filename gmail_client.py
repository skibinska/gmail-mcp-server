"""
Gmail API client for handling email operations.

This module provides a GmailClient class that simplifies Gmail API interactions
including authentication, reading emails, and creating draft replies.
"""

from __future__ import annotations

import os.path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

from utils.email_helpers import get_email_body, extract_reply_recipient, build_raw_email, header_value

SCOPES = [
    'https://www.googleapis.com/auth/gmail.readonly',
    'https://www.googleapis.com/auth/gmail.compose'
]

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(SCRIPT_DIR, 'token.json')

class GmailClient:
    def __init__(self):
        self.service = None
        self.authenticate()

    def authenticate(self) -> None:
        """
        Handle OAuth authentication and token management.

        Creates or refreshes Gmail API credentials, saving them to token.json
        for future use. Initiates OAuth flow if no valid credentials exist.
        """
        creds = None

        # Check if token.json exists
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        # If no valid credentials, let a user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for the next run
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

    def get_unread_emails(self, max_results=10):
        """
        Fetch unread emails from Gmail.

        Args:
            max_results: Maximum number of emails to retrieve (default: 10)

        Returns:
            List of email dictionaries containing id, subject, sender, etc.

        Raises:
            Exception: If Gmail API call fails
        """
        try:
            results = self.service.users().messages().list(
                userId='me',
                q='is:unread',
                maxResults=max_results
            ).execute()

            messages = results.get('messages', [])

            if not messages:
                return []

            emails = []
            for msg in messages:
                message = self.service.users().messages().get(
                    userId='me',
                    id=msg['id'],
                    format='full'
                ).execute()

                headers = message['payload']['headers']
                subject = next((h['value'] for h in headers if h['name'] == 'Subject'), 'No Subject')
                sender = next((h['value'] for h in headers if h['name'] == 'From'), 'Unknown')

                # Get email body
                body = get_email_body(message['payload'])

                emails.append({
                    'id': message['id'],
                    'threadId': message['threadId'],
                    'subject': subject,
                    'sender': sender,
                    'snippet': message.get('snippet', ''),
                    'body': body
                })

            return emails

        except Exception as e:
            print(f"Error fetching emails: {e}")
            return []

    def create_draft_reply(self, message_id: str, thread_id: str, reply_body: str) -> dict:
        """Creates a properly threaded draft reply to an existing message."""
        # Fetch full original message to get headers needed for reply
        original = self.service.users().messages().get(
            userId="me",
            id=message_id,
            format="metadata",
            metadataHeaders=["From", "Reply-To", "Subject", "Message-ID", "References"],
        ).execute()

        payload = original.get("payload", {})
        headers = payload.get("headers", [])

        to_addr = extract_reply_recipient(payload)

        if not to_addr:
            raise ValueError("Cannot create draft reply: could not extract a valid recipient from Reply-To/From")

        original_subject = header_value(headers, "Subject") or ""
        subject = original_subject if original_subject.lower().startswith("re:") else f"Re: {original_subject}".strip()

        # Threading headers
        in_reply_to = header_value(headers, "Message-ID") or None
        references = header_value(headers, "References") or None

        if in_reply_to:
            references = (references + " " + in_reply_to).strip() if references else in_reply_to

        raw = build_raw_email(
            to=to_addr,
            subject=subject,
            body=reply_body,
            in_reply_to=in_reply_to,
            references=references,
        )

        draft_body = {"message": {"raw": raw, "threadId": thread_id}}

        return self.service.users().drafts().create(userId="me", body=draft_body).execute()