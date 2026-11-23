"""Owner-only administrative commands."""
from config import OWNER_ID
from database.users import user_count
from database.credits import add
def register(bot):
    @bot.message_handler(commands=["stats"])
    def stats(m):
        if m.from_user.id!=OWNER_ID:bot.reply_to(m,"⛔ Not authorized.");return
        bot.reply_to(m,f"📊 Users: {user_count()}")
    @bot.message_handler(commands=["addcredits"])
    def addcredits(m):
        if m.from_user.id!=OWNER_ID:bot.reply_to(m,"⛔ Not authorized.");return
        p=(m.text or "").split()
        if len(p)!=3:bot.reply_to(m,"Usage: /addcredits USER_ID AMOUNT");return
        try:ok=add(int(p[1]),int(p[2]));bot.reply_to(m,"✅ Credits added." if ok else "User not found.")
        except ValueError:bot.reply_to(m,"Invalid user ID or amount.")
