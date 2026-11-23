"""Application composition root."""
from core.bot import bot
from database.initialization import init_db
from handlers.start import register as register_start
from handlers.admin import register as register_admin
def create_application():
    init_db()
    register_start(bot)
    register_admin(bot)
    return bot
