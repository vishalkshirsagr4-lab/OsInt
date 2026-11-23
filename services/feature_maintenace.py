


# Cache TTL: 30 seconds (fresh enough for admin changes to take effect quickly)
_maint_cache: dict = {}       # feature_key -> (is_maint, reason)
_maint_cache_ts: dict = {}    # feature_key -> timestamp
_MAINT_CACHE_TTL = 30         # seconds

def is_feature_maintenance(feature_key: str) -> tuple:
    """Returns (is_maintenance: bool, reason: str)"""
    now = time.time()
    if feature_key in _maint_cache:
        if now - _maint_cache_ts.get(feature_key, 0) < _MAINT_CACHE_TTL:
            return _maint_cache[feature_key]
    try:
        _mc = sqlite3.connect('bot.db', timeout=15)
        _cur = _mc.cursor()
        _cur.execute(
            "SELECT is_under_maintenance, reason FROM feature_maintenance WHERE feature_key=?",
            (feature_key,)
        )
        row = _cur.fetchone()
        _mc.close()
        result = (True, row[1] or '') if (row and row[0]) else (False, '')
        _maint_cache[feature_key] = result
        _maint_cache_ts[feature_key] = now
        return result
    except Exception:
        return False, ''

def set_feature_maintenance(feature_key: str, enable: bool, reason: str, admin_id: int) -> None:
    """Enable or disable maintenance mode for a feature."""
    _maint_cache.pop(feature_key, None)
    _maint_cache_ts.pop(feature_key, None)
    try:
        _mc = sqlite3.connect('bot.db', timeout=15)
        _cur = _mc.cursor()
        _cur.execute(
            "INSERT OR REPLACE INTO feature_maintenance (feature_key, is_under_maintenance, reason, set_by, set_at) VALUES (?,?,?,?,?)",
            (feature_key, 1 if enable else 0, reason, admin_id,
             _dt.now().strftime('%d %b %Y %I:%M %p'))
        )
        _mc.commit()
        _mc.close()
    except Exception as e:
        print(f"[maintenance] {e}")

def get_all_maintenance_status() -> dict:
    """Returns dict of feature_key -> (is_maintenance, reason)"""
    try:
        _mc = sqlite3.connect('bot.db', timeout=15)
        _cur = _mc.cursor()
        _cur.execute("SELECT feature_key, is_under_maintenance, reason FROM feature_maintenance")
        rows = _cur.fetchall()
        _mc.close()
        return {r[0]: (bool(r[1]), r[2] or '') for r in rows}
    except Exception:
        return {}

def maintenance_reply(bot_inst, message, feature_key: str) -> None:
    """Send maintenance message to user when feature is under maintenance."""
    _, reason = is_feature_maintenance(feature_key)
    label = _FEATURE_LABELS.get(feature_key, feature_key)
    reason_line = f"\n📝 <b>ᴄᴀᴜꜱᴇ:</b> {reason}" if reason else ""
    text = (
        f"🔧 <b>{label}</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"⚙️ <b>ᴛʜɪꜱ ꜰᴇᴀᴛᴜʀᴇ ɪꜱ ᴜɴᴅᴇʀ ᴍᴀɪɴᴛᴇɴᴀɴᴄᴇ</b>\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"🛠️ ʜᴀᴍ ɪꜱ ꜰᴇᴀᴛᴜʀᴇ ᴋᴏ ᴀᴩᴅᴀᴛᴇ ᴋᴀʀ ʀᴀʜᴇ ʜᴀɪɴ{reason_line}\n"
        f"⏳ ᴛʜᴏᴅɪ ᴅᴇʀ ᴍᴇɪɴ ᴡᴀᴩᴀꜱ ᴀᴀ ᴊᴀᴇɢᴀ!\n"
        f"━━━━━━━━━━━━━━━━━━\n"
        f"{BOT_CREDIT}"
    )
    bot_inst.reply_to(message, f"<blockquote>{text}</blockquote>", parse_mode='HTML')