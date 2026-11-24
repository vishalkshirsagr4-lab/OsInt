


# Old code overwrote messages matching the OLD default — wiped custom messages on restart
try:
    _mc = sqlite3.connect('bot.db', timeout=15)
    _mcc = _mc.cursor()
    _mcc.execute(
        "UPDATE bot_groups SET goodbye_message=? WHERE goodbye_message IS NULL",
        ('💥 Arre {name} chala gaya!\n━━━━━━━━━━━━━━━━━━\n🗓️ Left Date: {date}\n⏰ Left Time: {time} (IST)\n😤 {group} ke baad kahan jayega?\n🤧 Ruk tere par bomber pelta hun!\n━━━━━━━━━━━━━━━━━━',)
    )
    _mc.commit()
    _mc.close()
    print("✅ Goodbye messages initialized for NULL entries")
except Exception as _me:
    print(f"⚠️ Goodbye migration: {_me}")


def _ensure_group_settings_columns():
    """Run once at startup — adds missing columns to bot_groups."""
    global _grp_settings_migrated
    if _grp_settings_migrated:
        return
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        lcc = lc.cursor()
        for col_def in [
            'hitek_info_enabled INTEGER DEFAULT 1',
            'tg_bomber_enabled INTEGER DEFAULT 1',
            'bomber_enabled INTEGER DEFAULT 1',
            'free_info_mode INTEGER DEFAULT 0',
        ]:
            try:
                lcc.execute(f"ALTER TABLE bot_groups ADD COLUMN {col_def}")
                lc.commit()
            except Exception:
                pass
        lc.close()
        _grp_settings_migrated = True
    except Exception as e:
        print(f"⚠️ group settings migration: {e}")