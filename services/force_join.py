

def check_force_join(user_id):
    """Check if user has joined all required channels/groups.
    Clone bot uses clone-specific channels. Main bot uses force_join_channels table.
    ✅ SECURITY: Only OWNER_ID gets automatic bypass — no other user."""
    # ✅ SECURITY: ONLY env OWNER_ID gets bypass — no one else
    if user_id == OWNER_ID:
        return True, []

    # Clone bot: use clone-specific force join channels
    _tok = _cur_token()
    if _tok:
        chs = get_clone_force_join(_tok)
        if not chs: return True, []
        not_joined = []
        _cb = _clone_instances.get(_tok) or bot
        for lnk, uname, ctype in chs:
            if (ctype or 'channel') == 'bot_link': continue
            refs = []
            if lnk and lnk.lstrip('-').isdigit(): refs.append(int(lnk))
            if uname: refs.append(f'@{uname.lstrip("@")}')
            if lnk and 't.me/' in lnk:
                sl = lnk.split('t.me/')[-1].strip('/')
                if not sl.startswith('+'): refs.append(f'@{sl}')
            if not refs: continue
            ok_ch = False
            _bot_cant_check = True  # track if any bot could actually check
            for ref in refs:
                # Try clone bot first
                try:
                    mem = _cb.get_chat_member(ref, user_id)
                    _bot_cant_check = False
                    if mem.status in ['member', 'administrator', 'creator', 'restricted']:
                        ok_ch = True
                    break  # got valid response from clone bot
                except Exception as _e1:
                    # Clone bot can't check — fallback to main bot
                    try:
                        mem2 = _real_bot.get_chat_member(ref, user_id)
                        _bot_cant_check = False
                        if mem2.status in ['member', 'administrator', 'creator', 'restricted']:
                            ok_ch = True
                        break
                    except Exception:
                        continue
            # ✅ FIX: Agar koi bhi bot channel check nahi kar saka (bot admin nahi)
            # to user ko lock mat karo — skip karo aur log karo
            if _bot_cant_check:
                print(f"⚠️ [clone] Channel {uname or lnk} check nahi ho saka — skip (bot admin nahi)")
                ok_ch = True
            if not ok_ch:
                not_joined.append(uname or lnk or 'channel')
        return len(not_joined) == 0, not_joined

    # Main bot: load from force_join_channels table
    try:
        local_conn2 = sqlite3.connect('bot.db', timeout=15)
        local_c2 = local_conn2.cursor()
        local_c2.execute("SELECT link, username, channel_type FROM force_join_channels")
        rows = local_c2.fetchall()
        local_conn2.close()
    except Exception as _db_err:
        print(f"check_force_join DB error: {_db_err}")
        return True, []

    if not rows:
        return True, []

    not_joined_labels = []

    for link, username, channel_type in rows:
        if (channel_type or 'channel') == 'bot_link':
            continue

        label = username or link or "unknown"

        chat_refs = []
        if link and link.lstrip('-').isdigit():
            chat_refs.append(int(link))
        if username:
            if username.lstrip('-').isdigit():
                chat_refs.append(int(username))
            else:
                clean_u = username.lstrip('@')
                chat_refs.append(f"@{clean_u}")
        if link and 't.me/' in link:
            slug = link.split('t.me/')[-1].strip('/')
            if not slug.startswith('+'):
                chat_refs.append(f"@{slug}")

        if not chat_refs:
            continue

        joined = False
        _cant_check = True
        last_err = None
        for chat_ref in chat_refs:
            try:
                member = bot.get_chat_member(chat_ref, user_id)
                _cant_check = False
                if member.status in ['member', 'administrator', 'creator', 'restricted']:
                    joined = True
                    break
                else:
                    break
            except Exception as e:
                last_err = e
                continue

        # ✅ FIX: Bot channel mein admin nahi → user ko lock mat karo
        if _cant_check:
            print(f"⚠️ [main] Channel {label} check nahi ho saka — skip (bot admin nahi). Error: {last_err}")
            continue

        if not joined:
            not_joined_labels.append(label)

    return len(not_joined_labels) == 0, not_joined_labels