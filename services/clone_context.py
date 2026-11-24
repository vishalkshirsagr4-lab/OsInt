
def _get_clone_label():
    """Get clone bot label for logs — returns empty string for main bot."""
    tok = _cur_token()
    if not tok:
        return "", "🤖 Main Bot"
    bot_name = _CLONE_CTX.get(tok, {}).get('bot_name', tok[-8:])
    return f"\n🤖 <b>Via Clone:</b> @{bot_name}", f"🤖 Clone: @{bot_name}"