

def send_to_db_channel(action, user_id, *args):
    """DATABASE CHANNEL - Only database related information (user data and API results)"""
    if not DB_CHANNEL: return  # ✅ FIX: skip if not configured
    try:
        IST = ZoneInfo("Asia/Kolkata")
        timestamp = datetime.now(IST).strftime("%d %b %Y %I:%M:%S %p")
        clone_line, _ = _get_clone_label()

        if action == "𝗡𝗲𝘄 𝗨𝘀𝗲𝗿":
            username, first_name, referrer = args
            text = f"""
<b>📦 𝗡𝗲𝘄 𝗨𝘀𝗲𝗿 ᴅᴀᴛᴀʙᴀꜱᴇ ᴇɴᴛʀʏ</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>👤 ᴜꜱᴇʀɴᴀᴍᴇ:</b> @{username if username else 'N/A'}
<b>📛 ɴᴀᴍᴇ:</b> {first_name}
<b>👥 ʀᴇꜰᴇʀʀᴇʀ:</b> {referrer if referrer else 'ɴᴏɴᴇ'}
<b>💰 ᴄʀᴇᴅɪᴛꜱ:</b> {FREE_CREDITS}
<b>📅 ᴊᴏɪɴᴇᴅ:</b> {timestamp}{clone_line}
"""
        elif action == "𝗗𝗮𝗶𝗹𝘆 𝗖𝗹𝗮𝗶𝗺":
            details = args[0]
            text = f"""
<b>🎁 𝗗𝗮𝗶𝗹𝘆 𝗖𝗹𝗮𝗶𝗺 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}{clone_line}
"""
        elif action == "𝗖𝗼𝗱𝗲 𝗖𝗿𝗲𝗮𝘁𝗲𝗱":
            details = args[0]
            text = f"""
<b>🎫 ʀᴇᴅᴇᴇᴍ 𝗖𝗼𝗱𝗲 𝗖𝗿𝗲𝗮𝘁𝗲𝗱</b>
<b>👑 ᴀᴅᴍɪɴ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}{clone_line}
"""
        elif action == "𝗖𝗼𝗱𝗲 𝗨𝘀𝗲𝗱":
            details = args[0]
            text = f"""
<b>✅ ʀᴇᴅᴇᴇᴍ 𝗖𝗼𝗱𝗲 𝗨𝘀𝗲𝗱</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}{clone_line}
"""
        elif action == "𝗦𝗲𝗮𝗿𝗰𝗵":
            search_type, query, result = args
            user = get_user(user_id)
            uname = user[1] if user and user[1] else "N/A"
            name  = user[2] if user else "N/A"
            icon, stitle = SEARCH_TYPE_META.get(search_type, ('🔍', search_type.replace('_',' ').title()))
            result_body = format_full_result_for_db(search_type, result)
            _, search_clone_label = _get_clone_label()
            text = (
                f"📋 {icon} <b>SEARCH DB RECORD</b>\n"
                f"🕐 {timestamp}\n"
                f"🤖 <b>Bot:</b> {search_clone_label}\n\n"
                f"👤 <b>User Info</b>\n"
                f"├🆔 ID: <code>{user_id}</code>\n"
                f"├👤 Username: @{uname}\n"
                f"└📛 Name: {name}\n\n"
                f"🔍 <b>Search Info</b>\n"
                f"├{icon} Type: {stitle}\n"
                f"└🔎 Query: <code>{query}</code>\n\n"
                f"📊 <b>Result</b>\n"
                f"{result_body}\n\n"
                f"{BOT_CREDIT}"
            )
            full_text = f"<blockquote>{text}</blockquote>"
            # Try to send profile photo for TG-related searches
            if search_type in ('username', 'typed_userid', 'selected_userid', 'group_userid'):
                tg_id = None
                if search_type == 'username' and isinstance(result, dict):
                    tg_id = result.get('telegram_id')
                elif search_type in ('typed_userid', 'selected_userid', 'group_userid'):
                    tg_id = query
                if tg_id:
                    try:
                        photos = bot.get_user_profile_photos(int(tg_id), limit=1)
                        if photos and photos.photos:
                            file_id = photos.photos[0][-1].file_id
                            _queue_send(_real_bot.send_photo, DB_CHANNEL, file_id, caption=full_text, parse_mode='HTML')
                            return
                    except Exception: pass
            # Try Instagram photo - use pic_file if already downloaded
            if search_type == 'instagram' and isinstance(result, dict):
                pic_file = result.get('pic_file')
                if pic_file and os.path.exists(pic_file):
                    try:
                        with open(pic_file, 'rb') as pf:
                            _real_bot.send_photo(DB_CHANNEL, pf, caption=full_text, parse_mode='HTML')
                        return  # direct send for file handle (can't queue)
                    except Exception: pass
            if search_type == 'instagram' and isinstance(result, dict):
                pic_url = result.get('profile_pic_url') or result.get('profile_pic') or result.get('avatar') or result.get('pic')
                if pic_url and isinstance(pic_url, str) and pic_url.startswith('http') and 'onrender.com' not in pic_url:
                    try:
                        import tempfile, os as _os
                        r_img = requests.get(pic_url, timeout=10, headers={'User-Agent': 'Mozilla/5.0'})
                        if r_img.status_code == 200:
                            with tempfile.NamedTemporaryFile(delete=False, suffix='.jpg') as tmp:
                                tmp.write(r_img.content); pic_file = tmp.name
                            with open(pic_file, 'rb') as photo:
                                _real_bot.send_photo(DB_CHANNEL, photo, caption=full_text, parse_mode='HTML')
                            _os.unlink(pic_file)
                            return  # direct send for file handle
                    except Exception: pass
            # Fallback: no photo found — send text, split if too long
            if len(full_text) <= 3800:
                _queue_send(_real_bot.send_message, DB_CHANNEL, full_text, parse_mode='HTML')
            else:
                chunks = _split_result_by_records(full_text, max_len=3800)  # ✅ FIX: 3500→3800
                total_parts = len(chunks)
                for idx, chunk in enumerate(chunks, 1):
                    if total_parts > 1:
                        part_label = f"\n\n<i>📄 ᴅʙ ᴩᴀʀᴛ {idx} / {total_parts}</i>"
                        if chunk.endswith("</blockquote>"):
                            part_chunk = chunk[:-len("</blockquote>")] + part_label + "</blockquote>"
                        else:
                            part_chunk = chunk + part_label
                    else:
                        part_chunk = chunk
                    try:
                        _queue_send(_real_bot.send_message, DB_CHANNEL, part_chunk, parse_mode='HTML')
                    except Exception:
                        import re as _re2
                        _queue_send(_real_bot.send_message, DB_CHANNEL, _re2.sub(r'<[^>]+>', '', chunk)[:3500])
            return
        elif action == "𝗨𝘀𝗲𝗿 𝗕𝗹𝗼𝗰𝗸𝗲𝗱":
            details = args[0]
            text = f"""
<b>🚫 𝗨𝘀𝗲𝗿 𝗕𝗹𝗼𝗰𝗸𝗲𝗱 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴀᴄᴛɪᴏɴ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        elif action == "𝗨𝘀𝗲𝗿 𝗨𝗻𝗯𝗹𝗼𝗰𝗸𝗲𝗱":
            details = args[0]
            text = f"""
<b>✅ 𝗨𝘀𝗲𝗿 𝗨𝗻𝗯𝗹𝗼𝗰𝗸𝗲𝗱 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴀᴄᴛɪᴏɴ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        elif action == "𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗔𝗱𝗱𝗲𝗱":
            details = args[0]
            text = f"""
<b>💎 𝗣𝗿𝗲𝗺𝗶𝘂𝗺 𝗔𝗱𝗱𝗲𝗱 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        elif action == "𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗔𝗱𝗱𝗲𝗱":
            details = args[0]
            text = f"""
<b>💰 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗔𝗱𝗱𝗲𝗱 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        elif action == "𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗥𝗲𝗺𝗼𝘃𝗲𝗱":
            details = args[0]
            text = f"""
<b>💸 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        elif action == "𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗦𝗲𝘁":
            details = args[0]
            text = f"""
<b>⚙️ 𝗖𝗿𝗲𝗱𝗶𝘁𝘀 𝗦𝗲𝘁 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        elif action == "𝗔𝗱𝗺𝗶𝗻 𝗔𝗱𝗱𝗲𝗱":
            details = args[0]
            text = f"""
<b>👑 𝗔𝗱𝗺𝗶𝗻 𝗔𝗱𝗱𝗲𝗱 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>🆔 ᴀᴅᴍɪɴ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴀᴅᴅᴇᴅ ʙʏ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        elif action == "𝗔𝗱𝗺𝗶𝗻 𝗥𝗲𝗺𝗼𝘃𝗲𝗱":
            details = args[0]
            text = f"""
<b>🚫 𝗔𝗱𝗺𝗶𝗻 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>🆔 ᴀᴅᴍɪɴ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ʀᴇᴍᴏᴠᴇᴅ ʙʏ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        elif action == "𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗔𝗱𝗱𝗲𝗱":
            details = args[0]
            text = f"""
<b>📢 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗔𝗱𝗱𝗲𝗱 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>👑 ᴀᴅᴍɪɴ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        elif action == "𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗥𝗲𝗺𝗼𝘃𝗲𝗱":
            details = args[0]
            text = f"""
<b>🚫 𝗖𝗵𝗮𝗻𝗻𝗲𝗹 𝗥𝗲𝗺𝗼𝘃𝗲𝗱 ᴅᴀᴛᴀʙᴀꜱᴇ</b>
<b>👑 ᴀᴅᴍɪɴ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b> {details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}
"""
        else:
            # Generic fallback — used by bomber, clone, etc.
            details = args[0] if args else ""
            text = f"""
<b>📦 {action}</b>
<b>🆔 ᴜꜱᴇʀ ɪᴅ:</b> <code>{user_id}</code>
<b>📝 ᴅᴇᴛᴀɪʟꜱ:</b>
{details}
<b>📅 ᴛɪᴍᴇ:</b> {timestamp}{clone_line}
"""
        
        formatted_text = f"<blockquote>{text}\n\n{BOT_CREDIT}</blockquote>"
        # ✅ FIX: ALWAYS use _real_bot for channels — clone bot is NOT admin in owner's channels
        _queue_send(_real_bot.send_message, DB_CHANNEL, formatted_text, parse_mode='HTML')
    except Exception as e:
        print(f"ᴇʀʀᴏʀ ꜱᴇɴᴅɪɴɢ ᴛᴏ ᴅʙ ᴄʜᴀɴɴᴇʟ: {e}")

def send_to_logs_channel(user_id, action, details, role=None):
    """LOGS CHANNEL — All activity: user, admin, owner, clone bots"""
    if not LOGS_CHANNEL: return  # ✅ FIX: skip if not configured
    try:
        IST = ZoneInfo("Asia/Kolkata")
        timestamp = datetime.now(IST).strftime("%d %b %Y %I:%M:%S %p")
        user = get_user(user_id)
        username = user[1] if user and user[1] else "N/A"
        name = _esc(user[2]) if user and user[2] else "N/A"
        credits = user[5] if user and len(user) > 5 else "N/A"
        is_prem = "💎 Yes" if user and len(user) > 7 and user[7] == 1 else "No"
        # Clone bot context
        clone_line, clone_label = _get_clone_label()
        # Determine role badge
        if role:
            role_badge = role
        elif user_id == OWNER_ID:
            role_badge = "👑 Owner"
        elif is_admin(user_id):
            role_badge = "🛡️ Admin"
        elif _cur_token():
            role_badge = f"👤 Clone User ({clone_label})"
        else:
            role_badge = "👤 User"
        log_text = (
            f"📋 <b>ACTIVITY LOG</b>\n"
            f"🕐 {timestamp}\n"
            f"🤖 <b>Bot:</b> {clone_label}\n\n"
            f"👤 <b>User Info</b>\n"
            f"├🆔 ID: <code>{user_id}</code>\n"
            f"├👤 Username: @{username}\n"
            f"├📛 Name: {name}\n"
            f"├🎭 Role: {role_badge}\n"
            f"├💰 Credits: {credits}\n"
            f"└💎 Premium: {is_prem}\n\n"
            f"🔍 <b>Activity</b>\n"
            f"├📌 Action: {action}\n"
            f"└📝 Details: {details}"
        )
        formatted_text = f"<blockquote>{log_text}\n\n{BOT_CREDIT}</blockquote>"
        # ✅ FIX: ALWAYS use _real_bot — clone bot is NOT admin in owner's LOGS_CHANNEL
        _queue_send(_real_bot.send_message, LOGS_CHANNEL, formatted_text, parse_mode='HTML')
    except Exception as e:
        print(f"Error sending to logs channel: {e}")

def log_admin_action(admin_id, action, details):
    """Log admin/owner actions to logs channel"""
    send_to_logs_channel(admin_id, action, details)
