


def _clone_name(token):
    try:
        cb = _clone_instances.get(token)
        if cb:
            me = cb.get_me()
            return f"@{me.username}" if me.username else f"Bot#{me.id}"
    except Exception: pass
    return f"...{token[-8:]}"