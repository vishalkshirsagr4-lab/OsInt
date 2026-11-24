

def clone_is_premium(clone_token, user_id):
    """Check premium from MAIN users table — same premium on all bots."""
    user = get_user(user_id)
    return _is_effectively_premium(user, user_id)

def clone_add_premium(clone_token, user_id, days):
    """Add premium in MAIN users table — shared across all bots."""
    lc = sqlite3.connect('bot.db', timeout=15)
    try:
        lcc = lc.cursor()
        lcc.execute("SELECT is_premium, premium_until FROM users WHERE user_id=?", (user_id,))
        r = lcc.fetchone()
        now_dt = datetime.now()
        start_from = now_dt
        if r and r[0] == 1 and r[1]:
            try:
                existing = datetime.strptime(r[1], "%Y-%m-%d %H:%M:%S")
                if existing > now_dt: start_from = existing
            except Exception: pass
        until = start_from + timedelta(days=days)
        until_str = until.strftime("%Y-%m-%d %H:%M:%S")
        lcc.execute("UPDATE users SET is_premium=1, premium_until=? WHERE user_id=?", (until_str, user_id))
        lc.commit()
        trigger_backup_soon()
        return True, until_str
    except Exception as e:
        return False, str(e)
    finally:
        try: lc.close()
        except Exception: pass