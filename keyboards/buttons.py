from telebot.types import KeyboardButton, InlineKeyboardButton

class _StyledKB(KeyboardButton):
    """KeyboardButton subclass with style support for Bot API 9.4."""
    def __init__(self, text, style=None, **kwargs):
        super().__init__(text, **kwargs)
        self.__style = style  # double underscore = name mangled, safe

    def to_dict(self):
        d = super().to_dict()
        if self.__style:
            d['style'] = self.__style
        return d

class _StyledIKB(InlineKeyboardButton):
    """InlineKeyboardButton subclass with style support for Bot API 9.4."""
    def __init__(self, text, style=None, **kwargs):
        super().__init__(text, **kwargs)
        # Map 'active' → 'success' for inline buttons
        self.__style = 'success' if style == 'active' else style

    def to_dict(self):
        d = super().to_dict()
        if self.__style:
            d['style'] = self.__style
        return d

def _KB(text, style=None, **kwargs):
    """KeyboardButton factory — Bot API 9.4 style support.
    VALID VALUES: 'primary'(blue) | 'success'(green) | 'danger'(red)
    NOTE: 'active' is INVALID — use 'success' for green!"""
    # Map 'active' → 'success' (active is invalid, causes 400 error)
    if style == 'active':
        style = 'success'
    try:
        return _StyledKB(text, style=style, **kwargs)
    except Exception:
        try:
            return KeyboardButton(text, **kwargs)
        except Exception:
            return KeyboardButton(text)

def _IKB(text, style=None, **kwargs):
    """InlineKeyboardButton factory — Bot API 9.4 style support.
    Falls back to plain InlineKeyboardButton if subclass fails.
    ✅ FIX: url= kwarg is NEVER dropped — all fallbacks preserve it."""
    try:
        return _StyledIKB(text, style=style, **kwargs)
    except Exception:
        try:
            return InlineKeyboardButton(text, **kwargs)
        except Exception:
            # Now we properly preserve url= if present, else use callback_data
            if 'url' in kwargs:
                try:
                    return InlineKeyboardButton(text, url=kwargs['url'])
                except Exception:
                    pass
            return InlineKeyboardButton(text, callback_data=kwargs.get('callback_data', 'noop'))