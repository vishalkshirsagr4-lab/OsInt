"""Telegram bot construction.

This module only creates the TeleBot client. It does not start polling,
register application-specific handlers, or perform network requests at import
time. Keep handler registration and process lifecycle in their own modules.
"""

from __future__ import annotations

from functools import lru_cache
from typing import Optional

import telebot

from config import BOT_TOKEN


def create_bot(token: Optional[str] = None) -> telebot.TeleBot:
    """Create a configured Telegram bot client.

    Production uses the validated BOT_TOKEN from config.py. The optional
    override is intended for isolated tests.
    """
    resolved_token = (token or BOT_TOKEN or "").strip()
    if not resolved_token:
        raise RuntimeError(
            "BOT_TOKEN is missing. Set it in the deployment environment."
        )

    return telebot.TeleBot(
        resolved_token,
        parse_mode="HTML",
        threaded=True,
        num_threads=4,
    )


@lru_cache(maxsize=1)
def get_bot() -> telebot.TeleBot:
    """Return one process-wide client; this does not start polling."""
    return create_bot()


# Compatibility alias: creates the client but does not start polling.
bot = get_bot()
