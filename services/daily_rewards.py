

def claim_daily(user_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    today = datetime.now().strftime("%Y-%m-%d")
    try:
        local_c.execute("SELECT 1 FROM daily_claims WHERE user_id=? AND claim_date=?", (user_id, today))
        if local_c.fetchone():
            local_conn.close()
            return False
        local_c.execute("INSERT INTO daily_claims (user_id, claim_date) VALUES (?,?)", (user_id, today))
        local_c.execute("UPDATE users SET credits = credits + ? WHERE user_id = ?", (DAILY_CREDITS, user_id))
        local_conn.commit()
        local_conn.close()
        send_to_db_channel("𝗗𝗮𝗶𝗹𝘆 𝗖𝗹𝗮𝗶𝗺", user_id, f"+{DAILY_CREDITS} ᴄʀᴇᴅɪᴛꜱ")
        send_to_logs_channel(user_id, "🎁 ᴅᴀɪʟʏ ᴄʟᴀɪᴍ", f"+{DAILY_CREDITS} credits claimed")
        return True
    except Exception:
        try: local_conn.close()
        except Exception: pass
        return False