

def is_admin(user_id):
    if user_id == OWNER_ID:
        return True
    # Clone owner check — uses _CLONE_OWNERS (no thread-local needed!)
    # Works in lambda filters too (runs before handler wrapper)
    if user_id in _CLONE_OWNERS:
        return True
    # TTL cache check
    now = time.time()
    if user_id in _admin_cache:
        if now - _admin_cache_ts.get(user_id, 0) < _ADMIN_CACHE_TTL:
            return _admin_cache[user_id]
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    local_c.execute("SELECT user_id FROM admins WHERE user_id=?", (user_id,))
    result = local_c.fetchone()
    local_conn.close()
    val = result is not None
    _admin_cache[user_id] = val
    _admin_cache_ts[user_id] = now
    return val

def _is_main_admin_only(uid):
    """✅ SECURITY FIX: Sirf OWNER_ID (Render env se) ko admin panel access.
    DB-added admins ko full admin panel nahi milega — ye sabse important security fix hai.
    Clone owners ka alag panel hai (_is_clone_owner_only use karo)."""
    return uid == OWNER_ID


def is_owner(user_id):
    return user_id == OWNER_ID