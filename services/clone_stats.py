

def clone_get_stats(clone_token):
    """Get stats — counts from main users table who use this clone."""
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        # Count users who have interacted with this clone bot
        try:
            total = lcc.execute("SELECT COUNT(*) FROM clone_users WHERE clone_token=?", (clone_token,)).fetchone()[0]
        except Exception:
            total = 0
        today_s = datetime.now().strftime('%Y-%m-%d')
        try:
            new_today = lcc.execute("SELECT COUNT(*) FROM clone_users WHERE clone_token=? AND DATE(join_date)=?", (clone_token, today_s)).fetchone()[0]
        except Exception:
            new_today = 0
        now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            # Premium from main users table for clone users
            clone_user_ids = [r[0] for r in lcc.execute("SELECT user_id FROM clone_users WHERE clone_token=?", (clone_token,)).fetchall()]
        except Exception:
            clone_user_ids = []
        if clone_user_ids:
            placeholders = ','.join('?' * len(clone_user_ids))
            premium = lcc.execute(f"SELECT COUNT(*) FROM users WHERE user_id IN ({placeholders}) AND is_premium=1 AND premium_until>?",
                                  clone_user_ids + [now_str]).fetchone()[0]
            blocked = lcc.execute(f"SELECT COUNT(*) FROM users WHERE user_id IN ({placeholders}) AND is_blocked=1",
                                  clone_user_ids).fetchone()[0]
        else:
            premium = blocked = 0
        searches = lcc.execute("SELECT COUNT(*) FROM search_history WHERE user_id IN (SELECT user_id FROM clone_users WHERE clone_token=?)", (clone_token,)).fetchone()[0] if clone_user_ids else 0
        lc.close()
        return {'total': total, 'new_today': new_today, 'premium': premium, 'blocked': blocked, 'searches': searches}
    except Exception: return {'total': 0, 'new_today': 0, 'premium': 0, 'blocked': 0, 'searches': 0}
