"""SQLite connection helpers shared by the modular application."""
import os, sqlite3
from contextlib import contextmanager
DB_PATH=os.environ.get("DB_PATH","bot.db")
def connect():
    db=sqlite3.connect(DB_PATH,timeout=30)
    db.row_factory=sqlite3.Row
    db.execute("PRAGMA foreign_keys=ON")
    db.execute("PRAGMA busy_timeout=30000")
    return db
@contextmanager
def transaction():
    db=connect()
    try:
        with db: yield db
    finally: db.close()
