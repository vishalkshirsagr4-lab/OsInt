"""Pure parsing and formatting helpers for safe OsInt bot features."""
from __future__ import annotations

import hmac
import re

HELP_TEXT = (
    "OsInt bot is online.\n\n"
    "Available commands:\n"
    "/start — create or open your account\n"
    "/menu — show this menu\n"
    "/help — show help\n"
    "/balance — view your credits and referrals\n"
    "/daily — claim 1 daily credit\n"
    "/refer — get your referral link\n"
    "/redeem CODE — redeem a credit code\n"
    "/admin — owner-only tools\n"
    "/makecode CREDITS USES — owner-only redeem-code creation\n\n"
    "Private-person data lookups and spam tools are not part of this bot."
)

def parse_command(text: str) -> str:
    if not isinstance(text, str) or not text.strip():
        return ""
    first = text.strip().split(maxsplit=1)[0]
    if not first.startswith("/"):
        return ""
    return first.split("@", 1)[0].lower()

def command_args(text: str) -> list[str]:
    if not isinstance(text, str):
        return []
    parts = text.strip().split()
    return parts[1:] if len(parts) > 1 else []

def valid_webhook_secret(expected: str | None, supplied: str | None) -> bool:
    if not expected or not supplied:
        return False
    return hmac.compare_digest(str(expected), str(supplied))

def valid_positive_int(value: str, maximum: int = 1000000) -> int | None:
    if not re.fullmatch(r"[1-9][0-9]{0,6}", str(value or "")):
        return None
    number = int(value)
    return number if number <= maximum else None
