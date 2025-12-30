import re
from email.utils import parseaddr


def is_valid_email_address(value: str) -> bool:
    """Check if a string is a valid email address."""
    if not value:
        return False
    _, addr = parseaddr(value)
    return bool(addr) and ("@" in addr) and (" " not in addr)


def sanitize_single_recipient(recipient: str) -> str:
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

    return addr if addr and is_valid_email_address(addr) else ""
