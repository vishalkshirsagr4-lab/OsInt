import sqlite3 
from datetime import datetime, timedelta

def get_stats():
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    
    total = local_c.execute("SELECT COUNT(*) FROM users").fetchone()[0] or 0
    today = local_c.execute("SELECT COUNT(*) FROM users WHERE DATE(join_date)=DATE('now')").fetchone()[0] or 0
    searches = local_c.execute("SELECT COUNT(*) FROM search_history").fetchone()[0] or 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    premium = local_c.execute(
        "SELECT COUNT(*) FROM users WHERE is_premium=1 AND premium_until > ?", (now_str,)
    ).fetchone()[0] or 0
    blocked = local_c.execute("SELECT COUNT(*) FROM users WHERE is_blocked=1").fetchone()[0] or 0
    admins = local_c.execute("SELECT COUNT(*) FROM admins").fetchone()[0] or 0
    channels = local_c.execute("SELECT COUNT(*) FROM force_join_channels").fetchone()[0] or 0
    groups = local_c.execute("SELECT COUNT(*) FROM bot_groups").fetchone()[0] or 0
    
    active_today = 0
    try:
        active_today = local_c.execute("SELECT COUNT(*) FROM users WHERE DATE(last_active)=DATE('now')").fetchone()[0] or 0
    except Exception:
        active_today = 0
    
    local_conn.close()
    return total, today, searches, premium, blocked, active_today, admins, channels, groups