import sqlite3
import time

def _wal_checkpoint():
    """WAL flush — sab pending SQLite data bot.db mein likho."""
    try:
        _wc = sqlite3.connect('bot.db', timeout=10)
        _wc.execute("PRAGMA wal_checkpoint(TRUNCATE)")
        _wc.execute("PRAGMA optimize")
        _wc.commit()
        _wc.execute("PRAGMA wal_checkpoint(FULL)")
        _wc.commit()
        _wc.close()
        time.sleep(0.2)
    except Exception as e:
        print(f"[WAL] {e}")