

def _clone_owner_keyboard():
    """Full admin keyboard for clone bot owners."""
    mk = ReplyKeyboardMarkup(resize_keyboard=True, row_width=2)
    # Row 1 - Stats & Users
    mk.row(_KB("📊 ꜱᴛᴀᴛꜱ", style="primary"), _KB("👥 ᴜꜱᴇʀ ʟɪꜱᴛ", style="primary"))
    # Row 2 - Broadcast
    mk.row(_KB("📢 ʙʀᴏᴀᴅᴄᴀꜱᴛ", style="primary"), _KB("👤 ᴜꜱᴇʀ ɪɴꜰᴏ", style="primary"))
    # Row 3 - Block/Unblock
    mk.row(_KB("🚫 ʙʟᴏᴄᴋ ᴜꜱᴇʀ", style="danger"), _KB("✅ ᴜɴʙʟᴏᴄᴋ ᴜꜱᴇʀ", style="success"))
    # Row 4 - Credits
    mk.row(_KB("💰 ᴀᴅᴅ ᴄʀᴇᴅɪᴛꜱ", style="success"), _KB("💸 ʀᴇᴍᴏᴠᴇ ᴄʀᴇᴅɪᴛꜱ", style="danger"))
    mk.row(_KB("⚙️ ꜱᴇᴛ ᴄʀᴇᴅɪᴛꜱ", style="primary"), _KB("💎 ᴀᴅᴅ ᴩʀᴇᴍɪᴜᴍ", style="success"))
    mk.row(_KB("🚫 ʀᴇᴍᴏᴠᴇ ᴩʀᴇᴍɪᴜᴍ", style="danger"), _KB("🔍 ꜱᴇᴀʀᴄʜ ᴜꜱᴇʀ", style="primary"))
    # Row 5 - Redeem
    mk.row(_KB("🎫 ᴄʀᴇᴀᴛᴇ ʀᴇᴅᴇᴇᴍ", style="success"), _KB("📜 ʀᴇᴅᴇᴇᴍ ʟɪꜱᴛ", style="primary"))
    # Row 6 - Channels
    mk.row(_KB("📢 ᴄʜᴀɴɴᴇʟ ᴀᴅᴅ", style="success"), _KB("🗑️ ᴄʜᴀɴɴᴇʟ ʀᴇᴍᴏᴠᴇ", style="danger"))
    mk.row(_KB("📋 ᴄʜᴀɴɴᴇʟ ʟɪꜱᴛ", style="primary"), _KB("📤 ᴇxᴩᴏʀᴛ ᴜꜱᴇʀꜱ", style="primary"))
    # Row 7 - Navigation
    mk.row(_KB("🔙 ᴍᴀɪɴ ᴍᴇɴᴜ", style="primary"))
    return mk