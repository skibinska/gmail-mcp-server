"""
Gmail API client for handling email operations.

This module provides a GmailClient class that simplifies Gmail API interactions
including authentication, reading emails, and creating draft replies.
"""

from __future__ import annotations

import os.path
import base64
import re
from email.message import EmailMessage
from email.utils import parseaddr
from typing import Optional, Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/gmail.readonly',
          'https://www.googleapis.com/auth/gmail.compose']

# Get the directory where this script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
CREDENTIALS_PATH = os.path.join(SCRIPT_DIR, 'credentials.json')
TOKEN_PATH = os.path.join(SCRIPT_DIR, 'token.json')


class GmailClient:
    def __init__(self):
        self.service = None
        self.authenticate()

        """
        Handle OAuth authentication and token management.

        Creates or refreshes Gmail API credentials, saving them to token.json
        for future use. Initiates OAuth flow if no valid credentials exist.
        """
    def authenticate(self) -> None:
        creds = None

        # Check if token.json exists
        if os.path.exists(TOKEN_PATH):
            creds = Credentials.from_authorized_user_file(TOKEN_PATH, SCOPES)

        # If no valid credentials, let user log in
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    CREDENTIALS_PATH, SCOPES)
                creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(TOKEN_PATH, 'w') as token:
                token.write(creds.to_json())

        self.service = build('gmail', 'v1', credentials=creds)

        """
        Fetch unread emails from Gmail.

        Args:
            max_results: Maximum number of emails to retrieve (default: 10)

        Returns:
            List of email dictionaries containing id, subject, sender, etc.

        Raises:
            Exception: If Gmail API call fails
        """
    def get_unread_emails(self, max_results=10):
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
                body = self._get_email_body(message['payload'])

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

    def _get_email_body(self, payload : dict[str, Any]) -> str:
        """Extracts body from email payload"""
        body = ""

        if 'parts' in payload:
            for part in payload['parts']:
                if part['mimeType'] == 'text/plain':
                    if 'data' in part['body']:
                        body = base64.urlsafe_b64decode(part['body']['data']).decode('utf-8')
                        break
        elif 'body' in payload and 'data' in payload['body']:
            body = base64.urlsafe_b64decode(payload['body']['data']).decode('utf-8')

        return body[:500]  # Limit to 500 chars

    def _sanitize_single_recipient(self, recipient: str) -> str:
        """
        Return a single email address suitable for the To: header.
        Accepts inputs like 'Name <user@example.com>' or 'user@example.com'.
        Returns '' if nothing valid is found.
        """
        if not recipient:
            return ""

        # Prefer stdlib parsing for "Name <addr>" forms
        _name, addr = parseaddr(recipient.strip())
        addr = (addr or "").strip()

        # Some headers can be weirdly formatted; as a fallback, try to find an email-like token
        if not addr:
            m = re.search(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", recipient, flags=re.IGNORECASE)
            addr = m.group(0) if m else ""

        return addr if addr and self._is_valid_email_address(addr) else ""

    def _header_value(self, headers: list[dict], name: str) -> str:
        for h in headers or []:
            if h.get("name") == name:
                return h.get("value") or ""
        return ""

    def _is_valid_email_address(self, value: str) -> bool:
        if not value:
            return False
        _, addr = parseaddr(value)
        return bool(addr) and ("@" in addr) and (" " not in addr)

    def _extract_reply_recipient(self, message_payload: dict) -> str:
        """
        Extract the best reply recipient. Prefer Reply-To, else From.
        Returns a sanitized single email address or ''.
        """
        headers = (message_payload or {}).get("headers", [])

        reply_to_raw = self._header_value(headers, "Reply-To")
        from_raw = self._header_value(headers, "From")

        recipient = self._sanitize_single_recipient(reply_to_raw) or self._sanitize_single_recipient(from_raw)
        return recipient

    def _build_raw_email(
        self,
        to: str,
        subject: str,
        body: str,
        in_reply_to: Optional[str] = None,
        references: Optional[str] = None,
    ) -> str:
        """
        Build and return base64url encoded raw message.
        """
        to_sanitized = self._sanitize_single_recipient(to)
        if not to_sanitized:
            raise ValueError("Cannot create draft: extracted 'To' recipient is empty/invalid")

        msg = EmailMessage()
        msg["To"] = to_sanitized
        msg["Subject"] = subject or ""

        if in_reply_to:
            msg["In-Reply-To"] = in_reply_to
        if references:
            msg["References"] = references

        msg.set_content(body or "")

        raw_bytes = msg.as_bytes()
        return base64.urlsafe_b64encode(raw_bytes).decode("utf-8")

    def create_draft_reply(self, message_id: str, thread_id: str, reply_body: str) -> dict:
        """
        Creates a properly threaded draft reply to an existing message.
        """
        # Fetch full original message to get headers needed for reply
        original = self.service.users().messages().get(
            userId="me",
            id=message_id,
            format="metadata",
            metadataHeaders=["From", "Reply-To", "Subject", "Message-ID", "References"],
        ).execute()

        payload = original.get("payload", {})
        headers = payload.get("headers", [])

        to_addr = self._extract_reply_recipient(payload)

        if not to_addr:
            raise ValueError("Cannot create draft reply: could not extract a valid recipient from Reply-To/From")

        original_subject = self._header_value(headers, "Subject") or ""
        subject = original_subject if original_subject.lower().startswith("re:") else f"Re: {original_subject}".strip()

        # Threading headers
        in_reply_to = self._header_value(headers, "Message-ID") or None
        references = self._header_value(headers, "References") or None

        if in_reply_to:
            references = (references + " " + in_reply_to).strip() if references else in_reply_to

        raw = self._build_raw_email(
            to=to_addr,
            subject=subject,
            body=reply_body,
            in_reply_to=in_reply_to,
            references=references,
        )

        draft_body = {"message": {"raw": raw, "threadId": thread_id}}

        return self.service.users().drafts().create(userId="me", body=draft_body).execute()