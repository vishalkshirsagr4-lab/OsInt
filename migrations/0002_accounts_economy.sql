-- User accounts and safe bot economy features.
CREATE TABLE IF NOT EXISTS user_accounts (
    telegram_id TEXT PRIMARY KEY,
    username TEXT NOT NULL DEFAULT '',
    first_name TEXT NOT NULL DEFAULT '',
    credits INTEGER NOT NULL DEFAULT 5 CHECK (credits >= 0),
    referred_by TEXT,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    last_active TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (referred_by) REFERENCES user_accounts(telegram_id)
);

CREATE TABLE IF NOT EXISTS referrals (
    referrer_id TEXT NOT NULL,
    referred_id TEXT NOT NULL UNIQUE,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (referrer_id, referred_id),
    CHECK (referrer_id <> referred_id),
    FOREIGN KEY (referrer_id) REFERENCES user_accounts(telegram_id),
    FOREIGN KEY (referred_id) REFERENCES user_accounts(telegram_id)
);

CREATE TABLE IF NOT EXISTS daily_claims (
    telegram_id TEXT NOT NULL,
    claim_date TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (telegram_id, claim_date),
    FOREIGN KEY (telegram_id) REFERENCES user_accounts(telegram_id)
);

CREATE TABLE IF NOT EXISTS redeem_codes (
    code TEXT PRIMARY KEY,
    credits INTEGER NOT NULL CHECK (credits > 0),
    max_uses INTEGER NOT NULL CHECK (max_uses > 0),
    used_count INTEGER NOT NULL DEFAULT 0,
    expires_at TEXT NOT NULL,
    is_active INTEGER NOT NULL DEFAULT 1 CHECK (is_active IN (0, 1)),
    created_by TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT (datetime('now'))
);

CREATE TABLE IF NOT EXISTS redeemed_codes (
    telegram_id TEXT NOT NULL,
    code TEXT NOT NULL,
    redeemed_at TEXT NOT NULL DEFAULT (datetime('now')),
    PRIMARY KEY (telegram_id, code),
    FOREIGN KEY (telegram_id) REFERENCES user_accounts(telegram_id),
    FOREIGN KEY (code) REFERENCES redeem_codes(code)
);

CREATE TABLE IF NOT EXISTS credit_transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id TEXT NOT NULL,
    amount INTEGER NOT NULL,
    reason TEXT NOT NULL,
    reference TEXT NOT NULL DEFAULT '',
    created_at TEXT NOT NULL DEFAULT (datetime('now')),
    FOREIGN KEY (telegram_id) REFERENCES user_accounts(telegram_id)
);

CREATE INDEX IF NOT EXISTS idx_referrals_referrer ON referrals(referrer_id);
CREATE INDEX IF NOT EXISTS idx_credit_transactions_user ON credit_transactions(telegram_id, id DESC);
