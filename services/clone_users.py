

def clone_is_blocked(clone_token, user_id):
    """Check block status from MAIN users table — shared across all bots."""
    user = get_user(user_id)
    return bool(user and user[6] == 1)

def clone_block_user(clone_token, user_id, block=True):
    """Block/unblock user in MAIN users table — affects all bots."""
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        lc.execute("UPDATE users SET is_blocked=? WHERE user_id=?", (1 if block else 0, user_id))
        lc.commit(); lc.close(); trigger_backup_soon(); return True
    except Exception: return False


def clone_get_user_list(clone_token, limit=25):
    """Get user list from clone_users tracking table + main users data."""
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        # Get users who used this clone bot, with main bot data
        try:
            rows = lcc.execute("""
                SELECT u.user_id, u.first_name, u.username, u.credits, u.is_blocked, u.is_premium, cu.join_date
                FROM clone_users cu
                JOIN users u ON cu.user_id = u.user_id
                WHERE cu.clone_token=?
                ORDER BY cu.join_date DESC LIMIT ?
            """, (clone_token, limit)).fetchall()
        except Exception:
            # Fallback if clone_users tracking not available
            rows = lcc.execute("""SELECT user_id, first_name, username, credits, is_blocked, is_premium, join_date
                FROM users ORDER BY join_date DESC LIMIT ?""", (limit,)).fetchall()
        lc.close(); return rows
    except Exception: return []