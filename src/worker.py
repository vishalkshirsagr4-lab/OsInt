"""Cloudflare Python Worker entry point for OsInt."""
from __future__ import annotations

import logging
import secrets
from datetime import datetime, timedelta, timezone
from urllib.parse import urlparse

from js import JSON, Object, fetch
from pyodide.ffi import to_js
from workers import Response, WorkerEntrypoint

from bot_logic import HELP_TEXT, command_args, parse_command, valid_webhook_secret, valid_positive_int

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("osint-worker")
DAILY_CREDITS = 1
START_CREDITS = 5
REFERRAL_CREDITS = 1


def _field(value, key, default=None):
    if value is None:
        return default
    if isinstance(value, dict):
        return value.get(key, default)
    try:
        result = getattr(value, key)
        return default if result is None else result
    except Exception:
        try:
            result = value[key]
            return default if result is None else result
        except Exception:
            return default


async def _send_telegram_message(token: str, chat_id: int | str, text: str) -> None:
    endpoint = f"https://api.telegram.org/bot{token}/sendMessage"
    response = await fetch(
        endpoint,
        to_js(
            {
                "method": "POST",
                "headers": {"content-type": "application/json"},
                "body": JSON.stringify({"chat_id": chat_id, "text": text}),
            },
            dict_converter=Object.fromEntries,
        ),
    )
    if not response.ok:
        logger.error("Telegram sendMessage failed with HTTP %s", response.status)
        raise RuntimeError("Telegram message delivery failed")
    result = await response.json()
    if not result.ok:
        logger.error("Telegram rejected sendMessage (error_code=%s)", result.error_code)
        raise RuntimeError("Telegram message delivery failed")


class Default(WorkerEntrypoint):
    async def _run(self, sql: str, *params):
        return await self.env.DB.prepare(sql).bind(*params).run()

    async def _first(self, sql: str, *params):
        return await self.env.DB.prepare(sql).bind(*params).first()

    async def _ensure_user(self, user: dict, referred_by: str | None = None):
        uid = str(user.get("id", ""))
        if not uid:
            raise ValueError("Missing Telegram user ID")
        username = str(user.get("username") or "")
        first_name = str(user.get("first_name") or "")
        existing = await self._first(
            "SELECT telegram_id FROM user_accounts WHERE telegram_id = ?", uid
        )
        if not existing:
            referrer = None
            if referred_by and referred_by != uid:
                valid_ref = await self._first(
                    "SELECT telegram_id FROM user_accounts WHERE telegram_id = ?", referred_by
                )
                if valid_ref:
                    referrer = referred_by
            await self._run(
                """INSERT OR IGNORE INTO user_accounts
                   (telegram_id, username, first_name, credits, referred_by)
                   VALUES (?, ?, ?, ?, ?)""",
                uid, username, first_name, START_CREDITS, referrer,
            )
            if referrer:
                await self.env.DB.batch([
                    self.env.DB.prepare(
                        "INSERT OR IGNORE INTO referrals (referrer_id, referred_id) VALUES (?, ?)"
                    ).bind(referrer, uid),
                    self.env.DB.prepare(
                        """UPDATE user_accounts SET credits = credits + ?
                           WHERE telegram_id = ? AND changes() = 1"""
                    ).bind(REFERRAL_CREDITS, referrer),
                    self.env.DB.prepare(
                        """UPDATE user_accounts SET credits = credits + ?
                           WHERE telegram_id = ? AND changes() = 1"""
                    ).bind(REFERRAL_CREDITS, uid),
                ])
        await self._run(
            """UPDATE user_accounts SET username = ?, first_name = ?, last_active = datetime('now')
               WHERE telegram_id = ?""",
            username, first_name, uid,
        )
        return uid

    async def _balance_text(self, uid: str) -> str:
        row = await self._first(
            """SELECT credits, (SELECT COUNT(*) FROM referrals WHERE referrer_id = ?) AS referrals
               FROM user_accounts WHERE telegram_id = ?""",
            uid, uid,
        )
        if not row:
            return "Account not found. Send /start first."
        return (
            "💰 Your account\n"
            f"Credits: {_field(row, 'credits', 0)}\n"
            f"Successful referrals: {_field(row, 'referrals', 0)}"
        )

    async def _daily(self, uid: str) -> str:
        today = datetime.now(timezone.utc).date().isoformat()
        already_claimed = await self._first(
            "SELECT 1 AS claimed FROM daily_claims WHERE telegram_id = ? AND claim_date = ?",
            uid, today,
        )
        if already_claimed:
            return "You have already claimed today's reward. Come back tomorrow."
        await self.env.DB.batch([
            self.env.DB.prepare(
                "INSERT OR IGNORE INTO daily_claims (telegram_id, claim_date) VALUES (?, ?)"
            ).bind(uid, today),
            self.env.DB.prepare(
                """UPDATE user_accounts SET credits = credits + ?
                   WHERE telegram_id = ? AND changes() = 1"""
            ).bind(DAILY_CREDITS, uid),
            self.env.DB.prepare(
                """INSERT INTO credit_transactions (telegram_id, amount, reason, reference)
                   SELECT ?, ?, 'daily', ? WHERE changes() = 1"""
            ).bind(uid, DAILY_CREDITS, today),
        ])
        claimed = await self._first(
            "SELECT 1 AS claimed FROM daily_claims WHERE telegram_id = ? AND claim_date = ?",
            uid, today,
        )
        transaction = await self._first(
            """SELECT id FROM credit_transactions
               WHERE telegram_id = ? AND reason = 'daily' AND reference = ?""",
            uid, today,
        )
        if transaction:
            return f"🎁 Daily reward claimed: +{DAILY_CREDITS} credit.\n{await self._balance_text(uid)}"
        if claimed:
            return "You have already claimed today's reward. Come back tomorrow."
        return "Could not claim the daily reward. Please try again."

    async def _redeem(self, uid: str, code: str) -> str:
        normalized = code.strip().upper()
        if not normalized or len(normalized) > 40:
            return "Usage: /redeem CODE"
        await self.env.DB.batch([
            self.env.DB.prepare(
                """INSERT OR IGNORE INTO redeemed_codes (telegram_id, code)
                   SELECT ?, code FROM redeem_codes
                   WHERE code = ? AND is_active = 1 AND used_count < max_uses
                     AND expires_at > datetime('now')
                     AND NOT EXISTS (
                       SELECT 1 FROM redeemed_codes WHERE telegram_id = ? AND code = ?
                     )"""
            ).bind(uid, normalized, uid, normalized),
            self.env.DB.prepare(
                """UPDATE user_accounts SET credits = credits + (
                     SELECT credits FROM redeem_codes WHERE code = ?
                   ) WHERE telegram_id = ? AND changes() = 1"""
            ).bind(normalized, uid),
            self.env.DB.prepare(
                """UPDATE redeem_codes SET used_count = used_count + 1
                   WHERE code = ? AND changes() = 1"""
            ).bind(normalized),
            self.env.DB.prepare(
                """INSERT INTO credit_transactions (telegram_id, amount, reason, reference)
                   SELECT ?, credits, 'redeem', code FROM redeem_codes
                   WHERE code = ? AND changes() = 1"""
            ).bind(uid, normalized),
        ])
        redeemed = await self._first(
            "SELECT 1 AS redeemed FROM redeemed_codes WHERE telegram_id = ? AND code = ?",
            uid, normalized,
        )
        transaction = await self._first(
            "SELECT id FROM credit_transactions WHERE telegram_id = ? AND reason = 'redeem' AND reference = ?",
            uid, normalized,
        )
        if transaction:
            return f"✅ Code redeemed successfully.\n{await self._balance_text(uid)}"
        if redeemed:
            return "This code was already redeemed."
        return "Invalid, expired, or fully used code."

    async def _create_code(self, uid: str, args: list[str]) -> str:
        credits = valid_positive_int(args[0]) if len(args) >= 1 else None
        uses = valid_positive_int(args[1], 100000) if len(args) >= 2 else None
        if not credits or not uses:
            return "Usage: /makecode CREDITS USES"
        code = "OSINT-" + secrets.token_hex(3).upper()
        expires = (datetime.now(timezone.utc) + timedelta(days=30)).strftime("%Y-%m-%d %H:%M:%S")
        await self._run(
            """INSERT INTO redeem_codes (code, credits, max_uses, expires_at, created_by)
               VALUES (?, ?, ?, ?, ?)""",
            code, credits, uses, expires, uid,
        )
        return f"🎫 Redeem code created: {code}\nCredits: {credits} | Uses: {uses}\nExpires in 30 days."

    async def _handle_command(self, message: dict, token: str) -> str:
        user = message.get("from") or {}
        chat = message.get("chat") or {}
        text = message.get("text") or ""
        if not isinstance(user, dict) or not isinstance(chat, dict) or not isinstance(text, str):
            return ""
        # Ignore bot-authored messages to prevent bot-to-bot command loops.
        if user.get("is_bot"):
            return ""
        command = parse_command(text)
        if not command:
            return ""
        args = command_args(text)
        referred_by = None
        if command == "/start" and args and args[0].startswith("ref_"):
            candidate = args[0][4:]
            if candidate.isdigit():
                referred_by = candidate
        uid = await self._ensure_user(user, referred_by)
        if command == "/start":
            return f"Hello, {user.get('first_name') or 'there'}! 👋\nYour account is ready.\n\n{HELP_TEXT}"
        if command in {"/menu", "/help"}:
            return HELP_TEXT
        if command == "/balance":
            return await self._balance_text(uid)
        if command == "/daily":
            return await self._daily(uid)
        if command == "/refer":
            me = await fetch(
                f"https://api.telegram.org/bot{token}/getMe",
                to_js({"method": "GET"}, dict_converter=Object.fromEntries),
            )
            data = await me.json()
            bot_username = _field(_field(data, "result", {}), "username", "")
            if not bot_username:
                return "Could not get the bot username right now."
            count = await self._first(
                "SELECT COUNT(*) AS total FROM referrals WHERE referrer_id = ?", uid
            )
            return (
                f"Your referral link:\nhttps://t.me/{bot_username}?start=ref_{uid}\n"
                f"Successful referrals: {_field(count, 'total', 0)}\n"
                f"Reward: {REFERRAL_CREDITS} credit per new referred user."
            )
        if command == "/redeem":
            return await self._redeem(uid, args[0] if args else "")
        if command in {"/admin", "/makecode"}:
            owner_id = str(getattr(self.env, "OWNER_ID", "") or "")
            if not owner_id or uid != owner_id:
                return "⛔ Owner access only."
            if command == "/admin":
                return "🔐 Owner tools\n/makecode CREDITS USES — create a 30-day redeem code"
            return await self._create_code(uid, args)
        return "This command is not available. Use /menu to see supported commands."

    async def fetch(self, request):
        parsed = urlparse(request.url)
        path = parsed.path.rstrip("/") or "/"
        if request.method == "GET" and path == "/":
            return Response.json({
                "service": "OsInt", "runtime": "Cloudflare Workers (Python)",
                "status": "ok", "telegram_webhook": "/telegram/webhook",
            })
        if request.method == "GET" and path == "/health":
            try:
                await self.env.DB.prepare("SELECT 1 AS ok").run()
                return Response.json({"status": "ok", "database": "connected"})
            except Exception:
                logger.exception("D1 health check failed")
                return Response.json({"status": "degraded", "database": "unavailable"}, status=503)
        if path != "/telegram/webhook":
            return Response("Not Found", status=404)
        if request.method != "POST":
            return Response("Method Not Allowed", status=405)
        expected = getattr(self.env, "TELEGRAM_WEBHOOK_SECRET", None)
        supplied = request.headers.get("X-Telegram-Bot-Api-Secret-Token")
        if not valid_webhook_secret(expected, supplied):
            return Response("Unauthorized", status=401)
        token = getattr(self.env, "BOT_TOKEN", None)
        if not token:
            return Response("Bot is not configured", status=503)
        try:
            update = await request.json()
            if not isinstance(update, dict):
                return Response.json({"ok": True, "ignored": True})
            # Process only original messages. Edited commands must not replay
            # side effects such as creating additional redeem codes.
            message = update.get("message")
            if not isinstance(message, dict):
                return Response.json({"ok": True, "ignored": True})
            chat = message.get("chat") or {}
            chat_id = chat.get("id") if isinstance(chat, dict) else None
            if chat_id is None:
                return Response.json({"ok": True, "ignored": True})
            answer = await self._handle_command(message, token)
            if answer:
                await _send_telegram_message(token, chat_id, answer)
            return Response.json({"ok": True})
        except Exception:
            logger.exception("Telegram webhook processing failed")
            return Response("Webhook processing failed", status=500)
