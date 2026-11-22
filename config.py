import os


# ==================== BOT CONFIG ====================
# ⚠️ SECURITY FIX: Tokens environment variables se load ho rahe hain
# Render/Heroku/VPS par environment variables mein set karo:
#   BOT_TOKEN = "8872936013:AAFfjeSMwldDBAUn4UwiRrwcjGiU0yO8Y3c"
#   OWNER_ID  = "7981894574"
BOT_TOKEN = os.environ.get("BOT_TOKEN", "").strip()
if not BOT_TOKEN:
    raise RuntimeError("❌ BOT_TOKEN environment variable set nahi hai! Render > Environment mein BOT_TOKEN add karo.")

# ✅ OWNER_ID — hardcoded (env se override bhi ho sakta hai)
_owner_id_raw = os.environ.get("OWNER_ID", "").strip()
if not _owner_id_raw:
    raise RuntimeError("OWNER_ID environment variable is required.")
try:
    OWNER_ID = int(_owner_id_raw)
except ValueError as exc:
    raise RuntimeError("OWNER_ID must be a numeric Telegram user ID.") from exc

# Database and Logs Channel
DB_CHANNEL = os.environ.get("DB_CHANNEL", "-1003930518361").strip()
LOGS_CHANNEL = os.environ.get("LOGS_CHANNEL", "-1003930518361").strip()
if not DB_CHANNEL:
    print("⚠️ WARNING: DB_CHANNEL env var set nahi — DB logs disabled. Render > Environment mein DB_CHANNEL add karo.")
if not LOGS_CHANNEL:
    print("⚠️ WARNING: LOGS_CHANNEL env var set nahi — activity logs disabled. Render > Environment mein LOGS_CHANNEL add karo.")
