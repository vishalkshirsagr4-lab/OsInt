


# CLONE BOT RUNNER SYSTEM

# Tracks currently running clone bots: token -> thread
_clone_threads: dict = {}
# Stores live TeleBot instances for broadcast: token -> TeleBot instance
_clone_instances: dict = {}
# Stop flags: token -> True means "please stop"
_clone_stop_flags: dict = {}

def _run_clone_bot(token: str, owner_user_id: int) -> None:
    """
    Clone bot = Main bot EXACT same code on different token.
    Key fix: ALL callbacks (handlers + next_step + inline) are wrapped
    so bot.X() always routes to c_bot regardless of how they're called.
    """
    import telebot as _tb, threading as _th, functools as _ft

    # ── Init c_bot ──
    try:
        c_bot = _tb.TeleBot(token, threaded=False)
    except Exception as e:
        print(f"[clone] init error: {e}"); return

    try:
        _me = c_bot.get_me()
        _cn = _me.username or str(_me.id)
        print(f"[clone] @{_cn} started, owner={owner_user_id}")
        _clone_instances[token] = c_bot
    except Exception as e:
        print(f"[clone] bad token: {e}")
        _update_clone_status(token, 'invalid')
        try: _real_bot.send_message(owner_user_id, format_message(
            "<b>❌ Clone bot token invalid!</b>\nNaya token bhejo: /clonebot"), parse_mode='HTML')
        except Exception: pass
        return

    # ── Register clone context ──
    _CLONE_CTX[token] = {'owner_user_id': owner_user_id, 'bot_name': _cn}
    _CLONE_OWNERS[owner_user_id] = token

    # ── Wrapper: ensures bot.X() → c_bot.X() in ANY context ──
    def _wrap(fn):
        @_ft.wraps(fn)
        def _w(*a, **kw):
            _BOT_CTX.token = token
            _BOT_INSTANCE_CTX.instance = c_bot
            try:
                return fn(*a, **kw)
            finally:
                _BOT_CTX.token = None
                _BOT_INSTANCE_CTX.instance = None
        return _w

    for _attr in ('message_handlers', 'callback_query_handlers',
                  'chat_member_handlers', 'my_chat_member_handlers',
                  'edited_message_handlers', 'inline_handlers',
                  'chosen_inline_handlers', 'channel_post_handlers'):
        try:
            orig = getattr(_real_bot, _attr, [])
            setattr(c_bot, _attr, [dict(h, function=_wrap(h['function'])) for h in orig])
        except Exception: pass

    _orig_register = c_bot.register_next_step_handler
    def _wrapped_register(msg, callback, *args, **kwargs):
        return _orig_register(msg, _wrap(callback), *args, **kwargs)
    c_bot.register_next_step_handler = _wrapped_register

    if hasattr(c_bot, 'register_next_step_handler_by_chat_id'):
        _orig_reg2 = c_bot.register_next_step_handler_by_chat_id
        def _wrapped_register2(chat_id, callback, *args, **kwargs):
            return _orig_reg2(chat_id, _wrap(callback), *args, **kwargs)
        c_bot.register_next_step_handler_by_chat_id = _wrapped_register2

    _stop_event = _th.Event()
    _clone_stop_flags[token] = _stop_event

    def _do_polling():
        offset = None
        while not _stop_event.is_set():
            try:
                updates = c_bot.get_updates(
                    offset=offset, timeout=15,
                    long_polling_timeout=15,
                    allowed_updates=["message", "callback_query", "my_chat_member", "chat_member"])
                for u in updates:
                    if _stop_event.is_set(): break
                    offset = u.update_id + 1
                    try:
                        c_bot.process_new_updates([u])
                    except Exception as _pu:
                        print(f"[clone] @{_cn} update err: {_pu}")
            except Exception as e:
                if _stop_event.is_set(): break
                err = str(e).lower()
                if 'unauthorized' in err or '401' in err:
                    print(f"[clone] @{_cn} unauthorized — stopping")
                    _update_clone_status(token, 'stopped')
                    try: _real_bot.send_message(owner_user_id, format_message(
                        "<b>⚠️ Clone band ho gaya!</b>\nToken invalid. Naya bhejo: /clonebot"), parse_mode='HTML')
                    except Exception: pass
                    _stop_event.set(); break
                print(f"[clone] @{_cn} err: {e} — retry 3s")
                _stop_event.wait(3)

    _poll_thread = _th.Thread(target=_do_polling, daemon=True)
    _poll_thread.start()
    _poll_thread.join()

    _CLONE_CTX.pop(token, None)
    _CLONE_OWNERS.pop(owner_user_id, None)
    _clone_stop_flags.pop(token, None)
    _clone_instances.pop(token, None)
    _clone_threads.pop(token, None)
    print(f"[clone] @{_cn} thread ended cleanly")


def launch_clone_bot(token: str, owner_user_id: int) -> bool:
    """Start a clone bot thread if not already running. Returns True if launched."""
    if token in _clone_threads and _clone_threads[token].is_alive():
        return False  # Already running
    t = threading.Thread(target=_run_clone_bot, args=(token, owner_user_id), daemon=True)
    t.start()
    _clone_threads[token] = t
    return True

def resume_approved_clones() -> None:
    """On startup, re-launch all approved clone bots from DB."""
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        lcc = lc.cursor()
        lcc.execute("SELECT token, user_id FROM clone_bots WHERE status='approved' AND is_manually_stopped=0")
        rows = lcc.fetchall()
        lc.close()
        for token, user_id in rows:
            # Populate _CLONE_OWNERS so is_admin() works for clone owners on restart
            _CLONE_OWNERS[user_id] = token
            if token in _clone_threads and _clone_threads[token].is_alive():
                print(f"⚠️ Clone bot for user {user_id} already running — skip")
                continue
            t = threading.Thread(target=_run_clone_bot, args=(token, user_id), daemon=True)
            t.start()
            _clone_threads[token] = t
            print(f"🔄 Resumed clone bot for user {user_id}")
    except Exception as e:
        print(f"⚠️ resume_approved_clones: {e}")