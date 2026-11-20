CREATE TABLE IF NOT EXISTS bot_users (
    telegram_user_id TEXT PRIMARY KEY,
    username TEXT,
    first_name TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX IF NOT EXISTS idx_bot_users_last_seen
    ON bot_users(last_seen_at);
