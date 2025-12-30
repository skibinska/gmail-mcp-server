import base64
from typing import Any, Optional
from email.message import EmailMessage
from .validation import sanitize_single_recipient


def get_email_body(payload: dict[str, Any]) -> str:
    """Extracts body from email payload."""
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


def header_value(headers: list[dict], name: str) -> str:
    """Extract header value by name."""
    for h in headers or []:
        if h.get("name") == name:
            return h.get("value") or ""
    return ""


def extract_reply_recipient(message_payload: dict) -> str:
    """
    Extract the best reply recipient. Prefer Reply-To, else From.
    Returns a sanitized single email address or ''.
    """
    headers = (message_payload or {}).get("headers", [])

    reply_to_raw = header_value(headers, "Reply-To")
    from_raw = header_value(headers, "From")

    recipient = sanitize_single_recipient(reply_to_raw) or sanitize_single_recipient(from_raw)

    return recipient


def build_raw_email(
    to: str,
    subject: str,
    body: str,
    in_reply_to: Optional[str] = None,
    references: Optional[str] = None,
) -> str:
    """Build and return base64url encoded raw message."""
    to_sanitized = sanitize_single_recipient(to)
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
