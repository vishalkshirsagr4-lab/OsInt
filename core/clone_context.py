
import threading as _tl
_CLONE_CTX: dict = {}        # token -> {owner_user_id, bot_name}
_BOT_CTX = _tl.local()      # .token = current clone token (None = main bot)
_CLONE_OWNERS: dict = {}     # owner_uid -> token (for fast admin check without thread-local)

def _cur_token():
    return getattr(_BOT_CTX, 'token', None)

def _cur_owner():
    tok = _cur_token()
    if tok is None: return None
    return _CLONE_CTX.get(tok, {}).get('owner_user_id')