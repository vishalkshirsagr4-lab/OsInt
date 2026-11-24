

def _is_effectively_premium(user, uid):
    """Check premium status properly with expiry. Only OWNER_ID gets auto-premium."""
    if uid == OWNER_ID: return True
    if not user: return False
    if user[7] != 1: return False   # flag hi 0 hai
    if not user[8]: return False    # no expiry date = not premium
    try:
        return datetime.strptime(user[8], "%Y-%m-%d %H:%M:%S") > datetime.now()
    except Exception:
        return False