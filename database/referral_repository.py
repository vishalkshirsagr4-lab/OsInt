

def get_referral_count(user_id):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    local_c.execute("SELECT COUNT(*) FROM referrals WHERE referrer=?", (user_id,))
    result = local_c.fetchone()[0] or 0
    local_conn.close()
    return result