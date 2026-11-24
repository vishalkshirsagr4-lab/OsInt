


def save_search_history(user_id, search_type, query, result):
    local_conn = sqlite3.connect('bot.db', timeout=15)
    local_c = local_conn.cursor()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    try:
        result_json = json.dumps(result, default=str)
        # ✅ FIX: Feature-wise smart limit — hitek needs more space
        # DB channel gets full result regardless (sent before save)
        _MAX = {
            'hitek_full': 50000,   # 50KB — has lots of data
            'hitek_num':  30000,   # 30KB
            'mobile_number': 20000,# 20KB — can have many records
            'aadhar': 20000,
        }.get(search_type, 15000)  # Default 15KB for others
        if len(result_json) > _MAX:
            result_json = result_json[:_MAX] + '...[truncated]'
        local_c.execute("INSERT INTO search_history (user_id, search_type, query, search_date, result) VALUES (?,?,?,?,?)",
                 (user_id, search_type, query, timestamp, result_json))
        local_c.execute("UPDATE users SET total_searches = total_searches + 1, last_active = ? WHERE user_id = ?",
                       (timestamp, user_id))
        local_conn.commit()
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ꜱᴀᴠɪɴɢ ʜɪꜱᴛᴏʀʏ: {e}")
    finally:
        local_conn.close()
    # Run channel sends in background so they never block user-facing response
    def _bg():
        try:
            send_to_db_channel("𝗦𝗲𝗮𝗿𝗰𝗵", user_id, search_type, query, result)
        except Exception as e:
            print(f"[bg] db_channel error: {e}")
        try:
            send_to_logs_channel(user_id, "𝗦𝗲𝗮𝗿𝗰𝗵", f"{search_type}: {query}")
        except Exception as e:
            print(f"[bg] logs_channel error: {e}")
    threading.Thread(target=_bg, daemon=True).start()