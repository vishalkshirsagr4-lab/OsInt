

def load_channels_from_db():
    global FORCE_JOIN_LINKS, FORCE_JOIN_USERNAMES
    try:
        local_conn = sqlite3.connect('bot.db', timeout=15)
        local_c = local_conn.cursor()
        local_c.execute("SELECT link, username, channel_type FROM force_join_channels")
        channels = local_c.fetchall()
        local_conn.close()
        # Bot links skip karo — sirf channel/group verification ke liye
        real_channels = [ch for ch in channels if ch[2] != 'bot_link']
        new_links = [ch[0] for ch in real_channels]
        new_usernames = [ch[1] for ch in real_channels if ch[1] is not None]
        with _channels_lock:
            FORCE_JOIN_LINKS = new_links
            FORCE_JOIN_USERNAMES = new_usernames
    except Exception as e:
        print(f"⚠️ load_channels_from_db: {e}")