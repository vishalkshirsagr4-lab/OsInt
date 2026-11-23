"""Atomic credit operations."""
from database.connection import transaction,connect
def balance(user_id):
    db=connect()
    try:
        row=db.execute("SELECT credits FROM users WHERE user_id=?",(int(user_id),)).fetchone()
        return int(row[0]) if row else 0
    finally:db.close()
def add(user_id,amount):
    amount=int(amount)
    if amount<=0:raise ValueError("amount must be positive")
    with transaction() as db:
        return db.execute("UPDATE users SET credits=credits+? WHERE user_id=?",(amount,int(user_id))).rowcount==1
def deduct(user_id,amount=1):
    amount=int(amount)
    if amount<=0:raise ValueError("amount must be positive")
    with transaction() as db:
        return db.execute("UPDATE users SET credits=credits-? WHERE user_id=? AND credits>=?",(amount,int(user_id),amount)).rowcount==1
