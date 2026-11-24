


# ==================== CHANNEL LOGGING FUNCTIONS ====================

# ── Search type config: icon + title ──
SEARCH_TYPE_META = {
    'mobile_number':  ('📱', 'ɴᴜᴍʙᴇʀ ɪɴꜰᴏ'),
    'aadhar':         ('🪪', 'ᴀᴀᴅʜᴀʀ ɪɴꜰᴏ'),
    'username':       ('🔍', 'ᴜꜱᴇʀɴᴀᴍᴇ ɪɴꜰᴏ'),
    'selected_userid':('🆔', 'ꜱᴇʟᴇᴄᴛᴇᴅ ᴜꜱᴇʀ'),
    'typed_userid':   ('🆔', 'ᴛɢ ɪᴅ ɪɴꜰᴏ'),
    'userid':         ('🆔', 'ᴛɢ ɪᴅ ɪɴꜰᴏ'),
    'instagram':      ('📷', 'ɪɴꜱᴛᴀɢʀᴀᴍ ɪɴꜰᴏ'),
    'ifsc':           ('🏦', 'ɪꜰꜱᴄ ɪɴꜰᴏ'),
    'vehicle':        ('🚗', 'ᴠᴇʜɪᴄʟᴇ ɪɴꜰᴏ'),
    'gst':            ('💼', 'ɢꜱᴛ ɪɴꜰᴏ'),
    'email':          ('📧', 'ᴇᴍᴀɪʟ ɪɴꜰᴏ'),
    'upi':            ('💳', 'ᴜᴩɪ ɪɴꜰᴏ'),
    'pan':            ('🪪', 'ᴩᴀɴ ɪɴꜰᴏ'),
    'pak_num':        ('🇵🇰', 'ᴩᴀᴋ ɴᴜᴍ ɪɴꜰᴏ'),
    'pincode':        ('📍', 'ᴩɪɴᴄᴏᴅᴇ ɪɴꜰᴏ'),
    'ff_info':        ('🎮', 'ꜰʀᴇᴇ ꜰɪʀᴇ ɪɴꜰᴏ'),
    'ff':             ('🎮', 'ꜰʀᴇᴇ ꜰɪʀᴇ ɪɴꜰᴏ'),
    'hitek_num':      ('💎', 'ʜɪᴛᴇᴋ ɴᴜᴍ ɪɴꜰᴏ'),
    'hitek_full':     ('🌟', 'ʜɪᴛᴇᴋ ꜰᴜʟʟ ɪɴꜰᴏ'),
    'group_userid':   ('👥', 'ɢʀᴏᴜᴩ ᴜꜱᴇʀ ɪᴅ'),
}

SKIP_DB_KEYS = {'developer','Developer','DEVELOPER','dev','Dev','_raw','success','status','source','pic_file','freefire_id','timestamp','time'}

def _strip_emoji_from_key(k: str) -> str:
    """Strip leading emoji/symbol characters from an API key string"""
    cleaned = ''.join(
        ch for ch in str(k)
        if not (0x2600 <= ord(ch) <= 0x27BF or
                0x1F300 <= ord(ch) <= 0x1FAFF or
                0xFE00 <= ord(ch) <= 0xFE0F or
                ord(ch) == 0x200D)
    ).strip()
    return cleaned or str(k)

def _db_render_dict(d, depth=0):
    """Render dict/list into clean ├└ tree lines like aadhar UI"""
    SKIP_ALL = SKIP_DB_KEYS | {'n', 'key', 'apikey', 'msg', 'message', 'error', 'query', 'number'}
    EMPTY = (None, '', 'N/A', 'None', 'null', 'undefined', 'false', 'False', '0')

    def _collect_fields(rec):
        """Flatten one dict into (emoji, label, value) tuples, skip nested/junk"""
        fields = []
        seen = set()
        if not isinstance(rec, dict):
            return fields
        for k, v in rec.items():
            k_clean = _strip_emoji_from_key(k)
            kl = k_clean.lower().replace('_','').replace(' ','').replace('-','')
            skip_norm = {s.lower().replace('_','').replace(' ','') for s in SKIP_ALL}
            if kl in skip_norm or kl in seen:
                continue
            if isinstance(v, (dict, list)):
                continue
            if v in EMPTY:
                continue
            fv = format_value(v)
            if not fv:
                continue
            em = get_field_emoji(k_clean)
            pk = k_clean.replace('_',' ').replace('-',' ').title()
            fields.append((em, pk, fv))
            seen.add(kl)
        return fields

    lines = []
    if isinstance(d, list):
        valid = [i for i in d if isinstance(i, dict)]
        for idx, item in enumerate(valid, 1):
            if len(valid) > 1:
                lines.append(f"")
                lines.append(f"👤 <b>ʀᴇᴄᴏʀᴅ {idx}</b>")
            fields = _collect_fields(item)
            # Also expand one level of nested dicts
            for k, v in item.items():
                if isinstance(v, dict):
                    fields.extend(_collect_fields(v))
            for i, (em, pk, fv) in enumerate(fields):
                c = "└" if i == len(fields) - 1 else "├"
                lines.append(f"{c}{em} {pk}: <code>{fv}</code>")
    elif isinstance(d, dict):
        # check if it has list sub-records
        sub_lists = []
        for k, v in d.items():
            if isinstance(v, list) and str(k).lower().replace('_','') not in {s.lower().replace('_','') for s in SKIP_ALL}:
                sub_lists.extend([i for i in v if isinstance(i, dict)])
        if sub_lists:
            for idx, item in enumerate(sub_lists, 1):
                if len(sub_lists) > 1:
                    lines.append(f"")
                    lines.append(f"👤 <b>ʀᴇᴄᴏʀᴅ {idx}</b>")
                fields = _collect_fields(item)
                for i, (em, pk, fv) in enumerate(fields):
                    c = "└" if i == len(fields) - 1 else "├"
                    lines.append(f"{c}{em} {pk}: <code>{fv}</code>")
        else:
            fields = _collect_fields(d)
            # expand nested dicts
            for k, v in d.items():
                if isinstance(v, dict):
                    fields.extend(_collect_fields(v))
            for i, (em, pk, fv) in enumerate(fields):
                c = "└" if i == len(fields) - 1 else "├"
                lines.append(f"{c}{em} {pk}: <code>{fv}</code>")
    return lines

def format_full_result_for_db(search_type, result):
    """Format search result for DB channel — proper ├└ tree for all types"""
    if not result:
        return "<i>ɴᴏ ᴅᴀᴛᴀ</i>"

    icon, title = SEARCH_TYPE_META.get(search_type, ('🔍', search_type.replace('_',' ').title()))
    lines = [f"\n{icon} <b>{title.upper()}</b>", f"━━━━━━━━━━━━━━━━━━"]

    if search_type in ('mobile_number',):
        # result = {'success':T, 'data':[list of records]}
        records = result.get('data', []) if isinstance(result, dict) else []
        if isinstance(records, list):
            lines.append(f"📊 <b>ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ:</b> <b>{len(records)}</b>")
            lines.extend(_db_render_dict(records))
        else:
            lines.extend(_db_render_dict(result))

    elif search_type == 'aadhar':
        # result = {'success':T, 'aadhaar':'...', 'total_records':N, 'data':[list]}
        records = result.get('data', [])
        total   = result.get('total_records', len(records) if isinstance(records, list) else 0)
        lines.append(f"📊 <b>ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ:</b> <b>{total}</b>")
        lines.extend(_db_render_dict(records))

    elif search_type in ('username', 'selected_userid', 'typed_userid', 'group_userid'):
        lines.extend(_db_render_dict(result))

    elif search_type == 'instagram':
        # result = {id, username, name, full_name, bio, verified, private, followers, following, posts}
        d = result
        v = "✅" if d.get('verified') else "❌"
        p = "🔒" if (d.get('is_private') or d.get('private')) else "🔓"
        fields = [
            f"├👤 ᴜꜱᴇʀɴᴀᴍᴇ: <code>@{d.get('username','N/A')}</code>",
            f"├🆔 ᴜꜱᴇʀ ɪᴅ: <code>{d.get('id','N/A')}</code>",
        ]
        nm = d.get('name') or d.get('full_name','')
        if nm: fields.append(f"├📛 ɴᴀᴍᴇ: <b>{_esc(nm)}</b>")
        bio = d.get('bio','')
        if bio: fields.append(f"├📝 ʙɪᴏ: {_esc(bio)}")
        fields += [
            f"├✅ ᴠᴇʀɪꜰɪᴇᴅ: {v}",
            f"├🔒 ᴩʀɪᴠᴀᴛᴇ: {p}",
            f"├📊 ꜰᴏʟʟᴏᴡᴇʀꜱ: <code>{d.get('followers',0)}</code>",
            f"├🤝 ꜰᴏʟʟᴏᴡɪɴɢ: <code>{d.get('following',0)}</code>",
            f"├📸 ᴩᴏꜱᴛꜱ: <code>{d.get('posts',0)}</code>",
        ]
        if fields: fields[-1] = fields[-1].replace("├","└",1)
        lines.extend(fields)

    elif search_type == 'ifsc':
        # result = {ifsc, bank, branch, address, city, district, state, micr, contact, neft, rtgs, imps, upi}
        neft = "✅" if result.get('neft') else "❌"
        rtgs = "✅" if result.get('rtgs') else "❌"
        imps = "✅" if result.get('imps') else "❌"
        upi  = "✅" if result.get('upi')  else "❌"
        fields = []
        for k in ('ifsc','bank','branch','address','city','district','state','micr','contact'):
            v = result.get(k,'')
            if v and str(v).strip() not in ('N/A','None','','nan'):
                em = get_field_emoji(k)
                fields.append((em, k.replace('_',' ').title(), _esc(str(v))))
        for i,(em,pk,v) in enumerate(fields):
            c = "└" if i == len(fields)-1 else "├"
            lines.append(f"{c}{em} {pk}: <code>{v}</code>")
        lines.append(f"└💳 ɴᴇꜰᴛ:{neft}  ʀᴛɢꜱ:{rtgs}  ɪᴍᴩꜱ:{imps}  ᴜᴩɪ:{upi}")

    elif search_type == 'vehicle':
        # result = {'success':T, 'vehicle_data':merged_dict, ...}
        data = result.get('vehicle_data') or result.get('data') or result.get('_raw') or result
        lines.extend(_db_render_dict(data))

    elif search_type == 'pan':
        # result = {'success':T, 'pan':'...', 'data':{pan,fullname,message}, '_raw':...}
        raw = result.get('data') or result.get('_raw') or result
        if isinstance(raw, list): raw = raw[0] if raw else {}
        lines.extend(_db_render_dict(raw))

    elif search_type == 'pak_num':
        # result = {'success':T, 'data':[{address,cnic,n,name}], ...}
        records = result.get('data') or []
        if isinstance(records, list):
            lines.append(f"📊 <b>ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ:</b> <b>{len(records)}</b>")
            lines.extend(_db_render_dict(records))
        else:
            lines.extend(_db_render_dict(result))

    elif search_type == 'pincode':
        # result = {'success':T, 'data':[PostOffice records], ...}
        records = result.get('data') or []
        if isinstance(records, list):
            lines.append(f"📊 <b>ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ:</b> <b>{len(records)}</b>")
            lines.extend(_db_render_dict(records))
        else:
            lines.extend(_db_render_dict(result))

    elif search_type == 'upi':
        # result = {'success':T, 'name':'...', 'vpa':'...', 'acc_type':'...', 'ifsc':'...'}
        fields = []
        for k, label in [('vpa','UPI ID'),('name','Name'),('acc_type','Account Type'),
                         ('ifsc','IFSC'),('merchant','Merchant'),('valid','Status')]:
            v = result.get(k,'')
            if v: fields.append(f"├{get_field_emoji(k)} {label}: <code>{_esc(str(v))}</code>")
        if fields: fields[-1] = fields[-1].replace("├","└",1)
        lines.extend(fields)

    elif search_type in ('gst',):
        raw = result.get('_raw') or result.get('data') or result
        if isinstance(raw, list): raw = raw[0] if raw else {}
        lines.extend(_db_render_dict(raw))

    elif search_type == 'email':
        raw = result.get('_raw') or result.get('data') or result
        if isinstance(raw, list): raw = raw[0] if raw else {}
        lines.extend(_db_render_dict(raw))

    elif search_type in ('hitek_num', 'hitek_full'):
        raw_data = result.get('data') or result.get('_raw', {}).get('data') or []
        if isinstance(raw_data, dict): raw_data = [raw_data]
        if not raw_data:
            raw_data = [{k: v for k,v in result.items()
                         if k not in ('success','msg','query','number','_raw','region')
                         and v not in (None,'','N/A','None')}]
        lines.append(f"📊 <b>ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ:</b> <b>{len(raw_data)}</b>")
        lines.extend(_db_render_dict(raw_data))

    elif search_type == 'ff_info':
        info = result.get('_raw') or result.get('data') or result.get('player') or result
        lines.extend(_db_render_dict(info))

    else:
        # Generic fallback
        raw = result.get('_raw') or result.get('data') or result
        if isinstance(raw, list):
            lines.append(f"📊 <b>ᴛᴏᴛᴀʟ ʀᴇᴄᴏʀᴅꜱ:</b> <b>{len(raw)}</b>")
        lines.extend(_db_render_dict(raw))

    lines.append("━━━━━━━━━━━━━━━━━━")
    return "\n".join(lines)

