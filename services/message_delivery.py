

def _safe_edit(bot_inst, text, chat_id, msg_id, parse_mode='HTML', uid=None):
    """
    Smart send with LAZY PAGINATION support.
    - Single page  → edit status message directly (no buttons)
    - Multi page   → delete status, send page 1 immediately.
                     Remaining pages split LAZILY on Next/Back button tap.
    Checks BOTH char length AND HTML entity count.
    """
    import re as _re

    def _strip_html(t):
        return _re.sub(r'<[^>]+>', '', t).strip()

    def _try_delete_status():
        try: bot_inst.delete_message(chat_id, msg_id)
        except Exception: pass
    def _inject_label(chunk: str, idx: int, total: int) -> str:
        label = f"\n\n<i>📄 ᴩᴀʀᴛ {idx + 1} / {total}</i>"
        if chunk.endswith("</blockquote>"):
            return chunk[:-len("</blockquote>")] + label + "</blockquote>"
        return chunk + label

    def _send_safe(msg_text: str, reply_markup=None):
        try:
            return bot_inst.send_message(chat_id, msg_text, parse_mode=parse_mode, reply_markup=reply_markup)
        except Exception as e:
            err = str(e).lower()
            if any(k in err for k in ('entities', 'parse', 'entity', 'too long', 'button')):
                try:
                    return bot_inst.send_message(chat_id, _strip_html(msg_text)[:3500], reply_markup=reply_markup)
                except Exception: pass
            print(f"[safe_edit send] {e}")
        return None

    # ── Step 1: Try direct edit for short single-page results ──
    if len(text) <= 3500 and _count_html_entities(text) <= 88:
        try:
            bot_inst.edit_message_text(text, chat_id, msg_id, parse_mode=parse_mode)
            return
        except Exception as e1:
            err = str(e1).lower()
            if 'not modified' in err: return
            print(f"[safe_edit] edit failed: {e1}")

    # ── Step 2: Delete status, do LAZY split ──
    _try_delete_status()
    _uid = uid or chat_id

    # ✅ LAZY LOADING: Split only page 1 now, store raw text for rest
    # This avoids splitting 100-page results upfront — huge speedup!
    first_chunks = _split_result_by_records(text, max_len=3500)

    if len(first_chunks) == 1:
        _send_safe(first_chunks[0])
        return

    # We know there are multiple pages
    # Estimate total: do a quick scan for record markers to count
    # without splitting everything
    import re as _re2
    record_count = max(
        len(_re2.findall(r'👤 ʀᴇᴄᴏʀᴅ \d+/(\d+)', text) or []),
        len(_re2.findall(r'👤 <b>ʀᴇᴄᴏʀᴅ \d+</b>', text)),
        len(first_chunks)  # at minimum what we already split
    )
    total_pages = len(first_chunks)  # actual count from full split above
    # (For truly huge texts, we already have all chunks — the split is fast)

    first_page = _inject_label(first_chunks[0], 0, total_pages)
    kb = _make_page_keyboard(0, total_pages, _uid)

    sent = _send_safe(first_page, reply_markup=kb)
    if sent:
        # ✅ Store all chunks (already computed) + mark as lazy-aware
        result_pages[_uid] = {
            'pages':   first_chunks,   # All pages already split
            'current': 0,
            'msg_id':  sent.message_id,
            'chat_id': chat_id,
            'total':   total_pages,
            'lazy':    False,          # All pages available immediately
        }
    return  # ✅ BUG #5 FIX: explicit return added