

def expire_redeem_code(code):
    try:
        lc = sqlite3.connect('bot.db', timeout=15); lcc = lc.cursor()
        lcc.execute("UPDATE redeem_codes SET is_active=0, expires_at=? WHERE UPPER(code)=?", (datetime.now().strftime('%Y-%m-%d %H:%M:%S'), code.upper()))
        d = lcc.rowcount; lc.commit(); lc.close(); trigger_backup_soon()
        return (True, f"✅ Code {code.upper()} expired!") if d else (False, "❌ Code not found.")
    except Exception as e: return False, str(e)


# ==================== REDEEM CODE FUNCTIONS ====================

def generate_redeem_code(length=8):
    """Generate code in KOMAL-XXXX format"""
    chars = 'ABCDEFGHJKLMNPQRSTUVWXYZ'  # no I, O (look like 1, 0)
    suffix = ''.join(random.choice(chars) for _ in range(4))
    return f"OSINT-{suffix}"

def create_redeem_code(credits, max_uses, created_by, expires_days=30):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    code = generate_redeem_code()
    created_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    expires_at = (datetime.now() + timedelta(days=expires_days)).strftime("%Y-%m-%d %H:%M:%S")
    try:
        local_c.execute('''
            INSERT INTO redeem_codes (code, credits, max_uses, created_by, created_at, expires_at)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (code, credits, max_uses, created_by, created_at, expires_at))
        local_conn.commit()
        send_to_db_channel("𝗖𝗼𝗱𝗲 𝗖𝗿𝗲𝗮𝘁𝗲𝗱", created_by, f"ᴄᴏᴅᴇ: {code}, ᴄʀᴇᴅɪᴛꜱ: {credits}, ᴜꜱᴇꜱ: {max_uses}")
        send_to_logs_channel(created_by, "𝗖𝗼𝗱𝗲 𝗖𝗿𝗲𝗮𝘁𝗲𝗱", f"ᴄᴏᴅᴇ: {code}, ᴄʀᴇᴅɪᴛꜱ: {credits}, ᴜꜱᴇꜱ: {max_uses}")
        return code
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ᴄʀᴇᴀᴛɪɴɢ ʀᴇᴅᴇᴇᴍ ᴄᴏᴅᴇ: {e}")
        return None
    finally:
        try: local_conn.close()
        except Exception: pass
def use_redeem_code(user_id, code):
    # Two users cannot redeem same code simultaneously
    local_conn = sqlite3.connect('bot.db', timeout=30)
    local_c = local_conn.cursor()
    try:
        local_c.execute("BEGIN EXCLUSIVE")
        local_c.execute("SELECT id FROM redeemed_users WHERE user_id = ? AND code = ?", (user_id, code))
        if local_c.fetchone():
            local_conn.rollback()
            return {'success': False, 'reason': 'ALREADY_USED'}

        local_c.execute('''
            SELECT credits, max_uses, used_count, expires_at, COALESCE(is_active, 1)
            FROM redeem_codes WHERE UPPER(code) = UPPER(?)
        ''', (code,))
        result = local_c.fetchone()

        if not result:
            local_conn.rollback()
            return {'success': False, 'reason': 'INVALID_CODE'}

        credits, max_uses, used_count, expires_at, is_active = result

        if not is_active:
            local_conn.rollback()
            return {'success': False, 'reason': 'INVALID_CODE'}

        if not expires_at:
            local_conn.rollback()
            return {'success': False, 'reason': 'EXPIRED'}

        if datetime.now() > datetime.strptime(expires_at, "%Y-%m-%d %H:%M:%S"):
            local_conn.rollback()
            return {'success': False, 'reason': 'EXPIRED'}

        if used_count >= max_uses:
            local_conn.rollback()
            return {'success': False, 'reason': 'MAX_USES_REACHED'}

        # ✅ Atomic: all 3 updates in one transaction
        local_c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (credits, user_id))
        local_c.execute("UPDATE redeem_codes SET used_count = used_count + 1 WHERE UPPER(code) = UPPER(?)", (code,))
        local_c.execute("INSERT INTO redeemed_users (user_id, code, redeemed_at) VALUES (?, ?, ?)",
                       (user_id, code, datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        local_conn.commit()
        trigger_backup_soon()
        send_to_db_channel("𝗖𝗼𝗱𝗲 𝗨𝘀𝗲𝗱", user_id, f"ᴄᴏᴅᴇ: {code}, ᴄʀᴇᴅɪᴛꜱ: {credits}")
        send_to_logs_channel(user_id, "𝗖𝗼𝗱𝗲 𝗨𝘀𝗲𝗱", f"ᴄᴏᴅᴇ: {code}, ᴄʀᴇᴅɪᴛꜱ: {credits}")
        return {'success': True, 'credits': credits}
    except Exception as e:
        try: local_conn.rollback()
        except Exception: pass
        print(f"ᴇʀʀᴏʀ ᴜꜱɪɴɢ ᴄᴏᴅᴇ: {e}")
        return {'success': False, 'reason': 'ERROR'}
    finally:
        try: local_conn.close()
        except Exception: pass