import telebot
from config import BOT_TOKEN


_real_bot = telebot.TeleBot(BOT_TOKEN)


import threading as _proxy_tl
_BOT_INSTANCE_CTX = _proxy_tl.local()

class _BotProxy:
    """Thread-aware proxy — same global 'bot' works for both main + clone bots."""
    def __getattr__(self, name):
        inst = getattr(_BOT_INSTANCE_CTX, 'instance', None)
        return getattr(inst if inst is not None else _real_bot, name)
    def __setattr__(self, name, value):
        if name.startswith('_'):
            object.__setattr__(self, name, value)
            return
        inst = getattr(_BOT_INSTANCE_CTX, 'instance', None)
        setattr(inst if inst is not None else _real_bot, name, value)

bot = _BotProxy()