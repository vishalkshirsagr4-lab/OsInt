"""Cloudflare Python Worker entry point for the OsInt Telegram bot foundation.

This module intentionally contains no polling loop, local server, local files,
or private-personal-data lookup integrations.
"""
from __future__ import annotations

import logging
from urllib.parse import urlparse

from js import JSON, fetch
from workers import Response, WorkerEntrypoint

from bot_logic import reply_for, valid_webhook_secret

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("osint-worker")


async def _send_telegram_message(token: str, chat_id: int | str, text: str) -> None:
    """Send a Telegram message through the Workers fetch runtime."""
    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
    payload = {"chat_id": chat_id, "text": text}
    response = await fetch(
        endpoint,
        {
            "method": "POST",
            "headers": {"content-type": "application/json"},
            "body": JSON.stringify(payload),
        },
    )
    if not response.ok:
        # Do not log the URL: it contains the bot token.
        logger.error("Telegram sendMessage failed with HTTP %s", response.status)
        raise RuntimeError("Telegram message delivery failed")


class Default(WorkerEntrypoint):
    async def fetch(self, request):
        parsed = urlparse(request.url)
        path = parsed.path.rstrip("/") or "/"

        if request.method == "GET" and path == "/":
            return Response.json(
                {
                    "service": "OsInt",
                    "runtime": "Cloudflare Workers (Python)",
                    "status": "ok",
                    "telegram_webhook": "/telegram/webhook",
                }
            )

        if request.method == "GET" and path == "/health":
            try:
                await self.env.DB.prepare("SELECT 1 AS ok").run()
                return Response.json({"status": "ok", "database": "connected"})
            except Exception:
                logger.exception("D1 health check failed")
                return Response.json(
                    {"status": "degraded", "database": "unavailable"}, status=503
                )

        if path == "/telegram/webhook":
            if request.method != "POST":
                return Response("Method Not Allowed", status=405)

            expected = getattr(self.env, "TELEGRAM_WEBHOOK_SECRET", None)
            supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
            if not valid_webhook_secret(expected, supplied):
                return Response("Unauthorized", status=401)

            token = getattr(self.env, "BOT_TOKEN", None)
            if not token:
                logger.error("BOT_TOKEN secret is not configured")
                return Response("Bot is not configured", status=503)

            try:
                update = await request.json()
                message = update.get("message") or update.get("edited_message")
                if not isinstance(message, dict):
                    return Response.json({"ok": True, "ignored": True})

                sender = message.get("from") or {}
                chat = message.get("chat") or {}
                chat_id = chat.get("id")
                text = message.get("text") or ""
                if chat_id is None or not text:
                    return Response.json({"ok": True, "ignored": True})

                # Store only the Telegram account fields needed for ordinary bot
                # operation. Never store message contents or lookup queries.
                user_id = sender.get("id")
                if user_id is not None:
                    await self.env.DB.prepare(
                        """
                        INSERT INTO bot_users (telegram_user_id, username, first_name)
                        VALUES (?, ?, ?)
                        ON CONFLICT(telegram_user_id) DO UPDATE SET
                            username = excluded.username,
                            first_name = excluded.first_name,
                            last_seen_at = CURRENT_TIMESTAMP
                        """
                    ).bind(
                        str(user_id),
                        sender.get("username"),
                        sender.get("first_name"),
                    ).run()

                answer = reply_for(text, sender.get("first_name") or "")
                await _send_telegram_message(token, chat_id, answer)
                return Response.json({"ok": True})
            except Exception:
                logger.exception("Telegram webhook processing failed")
                return Response("Webhook processing failed", status=500)

        return Response("Not Found", status=404)
