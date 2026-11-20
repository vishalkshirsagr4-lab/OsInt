"""Small, side-effect-free Telegram command helpers for the Cloudflare Worker."""
from __future__ import annotations

import hmac


HELP_TEXT = (
    "OsInt bot is online.\n\n"
    "Available commands in this Cloudflare foundation:\n"
    "/start — start the bot\n"
    "/menu — show the menu\n"
    "/help — show help\n\n"
    "Other legacy features have not yet been migrated."
)


def parse_command(text: str) -> str:
    """Return a normalized Telegram command without its optional @bot suffix."""
    if not isinstance(text, str):
        return ""
    first = text.strip().split(maxsplit=1)[0] if text.strip() else ""
    if not first.startswith("/"):
        return ""
    return first.split("@", 1)[0].lower()


def reply_for(text: str, first_name: str = "") -> str:
    """Build replies only for the safe, migrated command set."""
    command = parse_command(text)
    name = first_name.strip() or "there"

    if command == "/start":
        return (
            f"Hello, {name}! 👋\n\n"
            "OsInt is running on Cloudflare. Use /menu to see available commands."
        )
    if command in {"/menu", "/help"}:
        return HELP_TEXT
    return (
        "This command is not available in the Cloudflare migration yet. "
        "Use /menu to see the commands currently supported."
    )


def valid_webhook_secret(expected: str | None, supplied: str | None) -> bool:
    """Compare Telegram's webhook secret without leaking it in logs."""
    if not expected or not supplied:
        return False
    return hmac.compare_digest(str(expected), str(supplied))
