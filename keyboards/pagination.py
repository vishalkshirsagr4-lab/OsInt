

def _make_page_keyboard(current: int, total: int, uid: int) -> InlineKeyboardMarkup:
    """Build Next/Back inline keyboard for result pagination."""
    kb = InlineKeyboardMarkup(row_width=3)
    buttons = []
    if current > 0:
        buttons.append(_IKB("⬅️ Back", callback_data=f"rpage:{uid}:{current - 1}", style="primary"))
    # Center: page indicator (non-clickable)
    buttons.append(_IKB(f"📄 {current + 1} / {total}", callback_data="rpage_noop", style="primary"))
    if current < total - 1:
        buttons.append(_IKB("Next ➡️", callback_data=f"rpage:{uid}:{current + 1}", style="primary"))
    kb.row(*buttons)
    return kb