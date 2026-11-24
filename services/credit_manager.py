

def deduct_credit(user_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("UPDATE users SET credits = MAX(0, credits - 1) WHERE user_id = ?", (user_id,))
        local_conn.commit()
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ᴅᴇᴅᴜᴄᴛɪɴɢ ᴄʀᴇᴅɪᴛ: {e}")
    finally:
        local_conn.close()

def add_credits(user_id, amount):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (amount, user_id))
        local_conn.commit()
        return True
    except Exception:
        return False
    finally:
        local_conn.close()

def remove_credits(user_id, amount):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("UPDATE users SET credits = credits - ? WHERE user_id = ? AND credits >= ?", (amount, user_id, amount))
        local_conn.commit()
        return local_c.rowcount > 0
    except Exception:
        return False
    finally:
        local_conn.close()

def set_credits(user_id, amount):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("UPDATE users SET credits = ? WHERE user_id = ?", (amount, user_id))
        local_conn.commit()
        return True
    except Exception:
        return False
    finally:
        local_conn.close()


def get_credits(user_id):
    """✅ SECURITY FIX: Infinite credits sirf OWNER_ID ke liye.
    Premium users ko bhi infinite nahi — unke credits zyada ho sakte hain lekin counted hote hain."""
    if user_id == OWNER_ID:
        return INFINITE_CREDITS
    user = get_user(user_id)
    if not user:
        return 0
    return user[5] or 0

def is_infinite_credits(credits_val):
    """Safe check: returns True if credits_val is infinite (admin/premium)."""
    return credits_val == INFINITE_CREDITS