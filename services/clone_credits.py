

def get_clone_credits(clone_token, user_id):
    """SHARED: Get credits from MAIN users table."""
    user = get_user(user_id)
    if user_id == OWNER_ID: return "∞"
    return user[5] if user else 0

def add_clone_credits(clone_token, user_id, amount):
    """SHARED: Add credits in MAIN users table."""
    return add_credits(user_id, amount)

def remove_clone_credits(clone_token, user_id, amount):
    """SHARED: Remove credits from MAIN users table."""
    return remove_credits(user_id, amount)

def set_clone_credits(clone_token, user_id, amount):
    """SHARED: Set credits in MAIN users table."""
    return set_credits(user_id, amount)


# get_credits defined below (line ~3225) — only one definition kept
# NOTE: add_credits / remove_credits / set_credits real implementations below at line ~1850

def clone_deduct_credit(clone_token, user_id, amount=1):
    """Deduct credit from MAIN users table."""
    remove_credits(user_id, amount)

def clone_claim_daily(clone_token, user_id):
    """Daily claim from MAIN daily_claims table — shared across all bots."""
    return claim_daily(user_id)