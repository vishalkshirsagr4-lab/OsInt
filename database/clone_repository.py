

def _update_clone_status(token: str, status: str) -> None:
    """Update status of a clone bot in DB."""
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        lcc = lc.cursor()
        lcc.execute("UPDATE clone_bots SET status=? WHERE token=?", (status, token))
        lc.commit()
        lc.close()
    except Exception as e:
        print(f"⚠️ _update_clone_status: {e}")


# ── Clone Helper Functions ──

def is_clone_admin(clone_token, user_id):
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        lcc.execute("SELECT 1 FROM clone_admins WHERE clone_token=? AND admin_user_id=?", (clone_token, user_id))
        r = lcc.fetchone(); lc.close(); return r is not None
    except Exception: return False

def get_clone_admins(clone_token):
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        lcc.execute("SELECT admin_user_id, added_by, added_date FROM clone_admins WHERE clone_token=? ORDER BY added_date", (clone_token,))
        r = lcc.fetchall(); lc.close(); return r
    except Exception: return []

def add_clone_admin(clone_token, admin_uid, added_by):
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        lcc.execute("INSERT OR IGNORE INTO clone_admins (clone_token,admin_user_id,added_by,added_date) VALUES (?,?,?,?)", (clone_token, admin_uid, added_by, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        lc.commit(); lc.close(); trigger_backup_soon()
        return True, "✅ Clone admin added!"
    except Exception as e: return False, str(e)

def remove_clone_admin(clone_token, admin_uid):
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        lcc.execute("DELETE FROM clone_admins WHERE clone_token=? AND admin_user_id=?", (clone_token, admin_uid))
        d = lcc.rowcount; lc.commit(); lc.close(); trigger_backup_soon()
        return (True,"✅ Removed!") if d else (False,"❌ Not found.")
    except Exception as e: return False, str(e)


def get_clone_force_join(clone_token):
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        lcc.execute("SELECT link,username,channel_type FROM clone_force_join WHERE clone_token=?", (clone_token,))
        r = lcc.fetchall(); lc.close(); return r
    except Exception: return []

def add_clone_force_join(clone_token, link, username, channel_type, added_by):
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        lcc.execute("INSERT OR IGNORE INTO clone_force_join (clone_token,link,username,channel_type,added_by,added_date) VALUES (?,?,?,?,?,?)", (clone_token, link, username, channel_type, added_by, datetime.now().strftime('%Y-%m-%d %H:%M:%S')))
        lc.commit(); lc.close(); trigger_backup_soon()
        return True, "✅ Channel added!"
    except Exception as e: return False, str(e)

def remove_clone_force_join(clone_token, inp):
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        lcc.execute("DELETE FROM clone_force_join WHERE clone_token=? AND (link=? OR username=?)", (clone_token, inp, inp))
        d = lcc.rowcount; lc.commit(); lc.close(); trigger_backup_soon()
        return (True,"✅ Removed!") if d else (False,"❌ Not found.")
    except Exception as e: return False, str(e)


def _get_all_clone_tokens():
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        lcc.execute("SELECT token, user_id FROM clone_bots WHERE status='approved'")
        r = lcc.fetchall(); lc.close(); return r
    except Exception: return []



# CLONE-SPECIFIC DATABASE FUNCTIONS
# Each clone bot has its own users, credits, premium, history etc.
# Main bot admin controls everything via main bot's admin panel.


def clone_get_user(clone_token, user_id):
    """Get user from MAIN users table — shared across all bots."""
    return get_user(user_id)

def clone_add_user(clone_token, user_id, username, first_name, referrer=None):
    """Add user to MAIN users table — shared across all bots."""
    return add_user(user_id, username, first_name, referrer)


def clone_save_search(clone_token, user_id, search_type, query, result=None):
    """Save search to MAIN search_history table — shared log."""
    save_search_history(user_id, search_type, query, result or {})


def clone_get_search_history(clone_token, limit=15):
    """Get recent search history for users of this clone bot."""
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        try:
            rows = lcc.execute("""
                SELECT sh.user_id, sh.search_type, sh.query, sh.search_date
                FROM search_history sh
                WHERE sh.user_id IN (SELECT user_id FROM clone_users WHERE clone_token=?)
                ORDER BY sh.search_date DESC LIMIT ?
            """, (clone_token, limit)).fetchall()
        except Exception:
            rows = lcc.execute("SELECT user_id, search_type, query, search_date FROM search_history ORDER BY search_date DESC LIMIT ?",
                               (limit,)).fetchall()
        lc.close(); return rows
    except Exception: return []

def clone_delete_search_history(clone_token):
    """Delete search history for users of this clone bot."""
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        try:
            clone_uids = [r[0] for r in lcc.execute("SELECT user_id FROM clone_users WHERE clone_token=?", (clone_token,)).fetchall()]
            if clone_uids:
                placeholders = ','.join('?' * len(clone_uids))
                lcc.execute(f"DELETE FROM search_history WHERE user_id IN ({placeholders})", clone_uids)
                lc.commit()
        except Exception: pass
        lc.close(); return True
    except Exception: return False