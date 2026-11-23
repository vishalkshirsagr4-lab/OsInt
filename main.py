"""Modular Telegram bot entry point."""
import os,threading
from core.application import create_application
from web.app import app
def main():
    bot=create_application()
    threading.Thread(target=lambda:app.run(host="0.0.0.0",port=int(os.environ.get("PORT","10000")),use_reloader=False),daemon=True).start()
    bot.infinity_polling(skip_pending=True,timeout=30,long_polling_timeout=25)
if __name__=="__main__":main()
