"""Safe user commands with stable command names."""
from telebot.types import InlineKeyboardMarkup,InlineKeyboardButton
from database.users import register_user,get_user
from database.credits import balance
def register(bot):
    @bot.message_handler(commands=["start"])
    def start(message):
        args=(message.text or "").split(maxsplit=1); ref=None
        if len(args)==2 and args[1].startswith("ref_"):
            try:ref=int(args[1][4:])
            except ValueError:pass
        u=message.from_user
        register_user(u.id,u.username or "",u.first_name or "",ref)
        kb=InlineKeyboardMarkup(row_width=2)
        kb.add(InlineKeyboardButton("💳 Credits",callback_data="account:credits"),InlineKeyboardButton("ℹ️ Help",callback_data="menu:help"))
        bot.reply_to(message,f"👋 Welcome {u.first_name or 'there'}!\n\nYour account is ready.\n💳 Credits: {balance(u.id)}",reply_markup=kb)
    @bot.message_handler(commands=["help"])
    def help_cmd(m):
        bot.reply_to(m,"📚 Commands\n/start — Open menu\n/help — Help\n/credits — Balance\n/daily — Daily reward\n/referral — Referral link\n\nLegacy restricted-action commands are not connected to private-data extraction, bombing, or unsolicited bulk messaging.")
    @bot.message_handler(commands=["credits","balance"])
    def credits_cmd(m):
        if not get_user(m.from_user.id):bot.reply_to(m,"Please use /start first.");return
        bot.reply_to(m,f"💳 Credits: {balance(m.from_user.id)}")
    @bot.message_handler(commands=["daily"])
    def daily(m):
        from datetime import date
        from database.connection import transaction
        with transaction() as db:
            try:db.execute("INSERT INTO daily_claims(user_id,claim_date) VALUES(?,?)",(m.from_user.id,date.today().isoformat()))
            except Exception:bot.reply_to(m,"You have already claimed today's reward.");return
            db.execute("UPDATE users SET credits=credits+1 WHERE user_id=?",(m.from_user.id,))
        bot.reply_to(m,"🎁 Daily reward claimed: +1 credit!")
    @bot.message_handler(commands=["referral"])
    def referral(m):
        me=bot.get_me()
        bot.reply_to(m,f"🔗 Your referral link:\nhttps://t.me/{me.username}?start=ref_{m.from_user.id}")
    @bot.callback_query_handler(func=lambda c:c.data in ("account:credits","menu:help"))
    def callbacks(c):
        if c.data=="account:credits":bot.answer_callback_query(c.id,f"Credits: {balance(c.from_user.id)}",show_alert=True)
        else:bot.answer_callback_query(c.id);bot.send_message(c.message.chat.id,"/start · /help · /credits · /daily · /referral")
