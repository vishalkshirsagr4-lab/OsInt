

def _send_clone_owner_panel(m):
    """Show limited admin panel for clone bot owner."""
    uid = m.from_user.id
    tok = _CLONE_OWNERS.get(uid) or _cur_token()
    if not tok: return
    # Get clone stats
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        total = lc.execute("SELECT COUNT(*) FROM clone_users WHERE clone_token=?", (tok,)).fetchone()[0]
        cu_ids = [r[0] for r in lc.execute("SELECT user_id FROM clone_users WHERE clone_token=?", (tok,)).fetchall()]
        lc.close()
        prem = blk = 0
        if cu_ids:
            lc2 = sqlite3.connect('bot.db', timeout=15)
            ph = ','.join('?'*len(cu_ids)); ns = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            prem = lc2.execute(f"SELECT COUNT(*) FROM users WHERE user_id IN ({ph}) AND is_premium=1 AND premium_until>?", cu_ids+[ns]).fetchone()[0]
            blk  = lc2.execute(f"SELECT COUNT(*) FROM users WHERE user_id IN ({ph}) AND is_blocked=1", cu_ids).fetchone()[0]
            lc2.close()
    except Exception: total = prem = blk = 0
    bot_name = _CLONE_CTX.get(tok, {}).get('bot_name', 'Clone Bot')
    # Extra stats
    try:
        lc3 = sqlite3.connect('bot.db', timeout=10)
        channels = lc3.execute("SELECT COUNT(*) FROM clone_force_join WHERE clone_token=?", (tok,)).fetchone()[0]
        today_users = lc3.execute("SELECT COUNT(*) FROM clone_users WHERE clone_token=? AND DATE(join_date)=DATE('now')", (tok,)).fetchone()[0]
        active_codes = lc3.execute("SELECT COUNT(*) FROM redeem_codes WHERE COALESCE(is_active,1)=1 AND expires_at>datetime('now')").fetchone()[0]
        is_running = tok in _clone_threads and _clone_threads[tok].is_alive()
        lc3.close()
    except Exception:
        channels = today_users = active_codes = 0; is_running = False
    IST = ZoneInfo("Asia/Kolkata")
    now_ist = datetime.now(IST)
    status_icon = "🟢 Running" if is_running else "🔴 Stopped"
    bot.send_message(m.chat.id, format_message(
        f"<b>⚙️ ᴄʟᴏɴᴇ ᴀᴅᴍɪɴ ᴩᴀɴᴇʟ</b>\n━━━━━━━━━━━━━━━━━━\n"
        f"🤖 <b>Bot:</b> @{bot_name}\n"
        f"📡 <b>Status:</b> {status_icon}\n"
        f"🕐 <b>Time:</b> {now_ist.strftime('%d %b %I:%M %p')}\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"👥 <b>Total Users:</b> <code>{total}</code>\n"
        f"📈 <b>Today Joined:</b> <code>{today_users}</code>\n"
        f"💎 <b>Premium:</b> <code>{prem}</code>\n"
        f"🚫 <b>Blocked:</b> <code>{blk}</code>\n"
        f"📢 <b>Channels:</b> <code>{channels}</code>\n"
        f"🎫 <b>Active Codes:</b> <code>{active_codes}</code>"
    ), reply_markup=_clone_owner_keyboard(), parse_mode='HTML')

