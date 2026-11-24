
def is_group(message):
    return message.chat.type in ['group', 'supergroup']


def _count_html_entities(text: str) -> int:
    """Count HTML tags (each open+close pair = 2 entities for Telegram)."""
    import re as _re
    return len(_re.findall(r'<[^>]+>', text))