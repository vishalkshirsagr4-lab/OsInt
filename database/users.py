"""User registration and account reads."""
from datetime import datetime
from database.connection import transaction,connect
def register_user(user_id,username="",first_name="",referrer=None):
    now=datetime.utcnow().strftime("%Y-%m-%d %H:%M:%S")
    uid=int(user_id); ref=int(referrer) if referrer and int(referrer)!=uid else None
    with transaction() as db:
        db.execute("INSERT OR IGNORE INTO users(user_id,username,first_name,join_date,referrer,credits) VALUES(?,?,?,?,?,10)",(uid,username or "",first_name or "",now,ref))
        if ref and not db.execute("SELECT 1 FROM referrals WHERE referred=?",(uid,)).fetchone():
            db.execute("INSERT INTO referrals(referrer,referred,date) VALUES(?,?,?)",(ref,uid,now))
            db.execute("UPDATE users SET credits=credits+1 WHERE user_id=?",(ref,))
        db.execute("UPDATE users SET username=?,first_name=?,last_active=? WHERE user_id=?",(username or "",first_name or "",now,uid))
def get_user(user_id):
    db=connect()
    try:return db.execute("SELECT * FROM users WHERE user_id=?",(int(user_id),)).fetchone()
    finally:db.close()
def user_count():
    db=connect()
    try:return db.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    finally:db.close()
