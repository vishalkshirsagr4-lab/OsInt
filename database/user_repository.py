


from dbm import sqlite3


def get_user(user_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    local_c.execute("SELECT * FROM users WHERE user_id=?", (user_id,))
    result = local_c.fetchone()
    local_conn.close()
    return result

def add_user(user_id, username, first_name, referrer=None):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    date = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        local_c.execute('''
            INSERT OR IGNORE INTO users 
            (user_id, username, first_name, join_date, referrer, credits, last_active) 
            VALUES (?,?,?,?,?,?,?)
        ''', (user_id, username, first_name, date, referrer, FREE_CREDITS, date))
        
        if local_c.rowcount > 0 and referrer and referrer != user_id:
            local_c.execute("INSERT OR IGNORE INTO referrals (referrer, referred, date) VALUES (?,?,?)",
                      (referrer, user_id, date))
            if local_c.rowcount > 0:
                local_c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (REFERRAL_CREDITS, referrer))
        
        local_conn.commit()
        tok = _cur_token()
        if tok and local_c.rowcount > 0:
            try:
                local_c.execute(
                    "INSERT OR IGNORE INTO clone_users (clone_token, user_id, username, first_name, join_date, last_active) VALUES (?,?,?,?,?,?)",
                    (tok, user_id, username, first_name, date, date)
                )
                local_conn.commit()
            except Exception: pass
        # Clone info for logging
        _tok_log = _cur_token()
        _bot_label = f"Clone @{_CLONE_CTX.get(_tok_log,{}).get('bot_name','?')}" if _tok_log else "Main Bot"
        send_to_db_channel("𝗡𝗲𝘄 𝗨𝘀𝗲𝗿", user_id, username, first_name, referrer)
        send_to_logs_channel(user_id, "𝗡𝗲𝘄 𝗨𝘀𝗲𝗿", f"ᴜꜱᴇʀɴᴀᴍᴇ: @{username}, ɴᴀᴍᴇ: {first_name}, ʀᴇꜰᴇʀʀᴇʀ: {referrer}, Bot: {_bot_label}")
        trigger_backup_soon()
        return True
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ᴀᴅᴅɪɴɢ ᴜꜱᴇʀ: {e}")
        return False
    finally:
        try: local_conn.close()
        except Exception: pass
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


def get_all_users():
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    local_c.execute("SELECT user_id FROM users WHERE is_blocked=0")
    result = local_c.fetchall()
    local_conn.close()
    return result