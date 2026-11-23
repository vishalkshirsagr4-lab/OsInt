
import sqlite3

def get_user(user_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    local_c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    result = local_c.fetchone()
    local_conn.close()
    return result

def update_user(user_id, **kwargs):
    ALLOWED_COLUMNS = {
        'username', 'first_name', 'join_date', 'referrer', 'credits',
        'is_blocked', 'is_premium', 'premium_until', 'joined_channels',
        'total_searches', 'last_active', 'money', 'clone_bots'
    }
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        for key, value in kwargs.items():
            if key not in ALLOWED_COLUMNS:
                print(f"⚠️ update_user: Invalid column '{key}' blocked!")
                continue
            local_c.execute(f"UPDATE users SET {key}=? WHERE user_id=?", (value, user_id))
        local_conn.commit()
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ᴜᴩᴅᴀᴛɪɴɢ ᴜꜱᴇʀ: {e}")
    finally:
        local_conn.close()


def get_referral_count(user_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    local_c.execute("SELECT COUNT(*) FROM referrals WHERE referrer=?", (user_id,))
    result = local_c.fetchone()[0] or 0
    local_conn.close()
    return result

def get_money(user_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("SELECT money FROM users WHERE user_id=?", (user_id,))
        r = local_c.fetchone()
        return r[0] if r else 0
    except Exception:
        return 0
    finally:
        local_conn.close()



def add_money(user_id, amount):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("UPDATE users SET money = money + ? WHERE user_id = ?", (amount, user_id))
        local_conn.commit()
    finally:
        local_conn.close()


def remove_money(user_id, amount):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("UPDATE users SET money = MAX(0, money - ?) WHERE user_id = ?", (amount, user_id))
        local_conn.commit()
    finally:
        local_conn.close()


def get_daily_claim_count(user_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("SELECT COUNT(*) FROM daily_claims WHERE user_id=?", (user_id,))
        r = local_c.fetchone()
        return r[0] if r else 0
    finally:
        local_conn.close()


def get_redeem_count(user_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    try:
        local_c.execute("SELECT COUNT(*) FROM redeemed_users WHERE user_id=?", (user_id,))
        r = local_c.fetchone()
        return r[0] if r else 0
    finally:
        local_conn.close()


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