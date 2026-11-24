

_STARTUP_RESTORED = _restore_db_from_github()
print(f"{'✅' if _STARTUP_RESTORED else '⚠️'} [STARTUP] DB: {'GitHub se restore hua ✅' if _STARTUP_RESTORED else 'Fresh/Local DB (pehla deploy ya GH config missing)'}")


def init_db():
    """Initialize DB connection and create all tables. Call after restore."""
    global conn, c
    if 'conn' in globals() and conn:
        try:
            conn.close()
        except Exception: pass
    conn = sqlite3.connect('bot.db', check_same_thread=False, timeout=30)
    c = conn.cursor()
    # ✅ WAL mode: Render par concurrent reads/writes ke liye zaroori
    try:
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA synchronous=NORMAL")
        conn.commit()
    except Exception: pass

    # Create tables if not exists
    c.executescript('''
    CREATE TABLE IF NOT EXISTS users (
        user_id INTEGER PRIMARY KEY,
        username TEXT,
        first_name TEXT,
        join_date TEXT,
        referrer INTEGER,
        credits INTEGER DEFAULT 10,
        is_blocked INTEGER DEFAULT 0,
        is_premium INTEGER DEFAULT 0,
        premium_until TEXT,
        joined_channels TEXT DEFAULT '[]',
        total_searches INTEGER DEFAULT 0
    );
    
    CREATE TABLE IF NOT EXISTS referrals (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        referrer INTEGER,
        referred INTEGER,
        date TEXT
    );
    
    CREATE TABLE IF NOT EXISTS search_history (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        search_type TEXT,
        query TEXT,
        search_date TEXT,
        result TEXT
    );
    
    CREATE TABLE IF NOT EXISTS daily_claims (
        user_id INTEGER,
        claim_date TEXT,
        PRIMARY KEY (user_id, claim_date)
    );
    
    CREATE TABLE IF NOT EXISTS redeem_codes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        code TEXT UNIQUE,
        credits INTEGER,
        max_uses INTEGER,
        used_count INTEGER DEFAULT 0,
        created_by INTEGER,
        created_at TEXT,
        expires_at TEXT
    );
    
    CREATE TABLE IF NOT EXISTS redeemed_users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        code TEXT,
        redeemed_at TEXT,
        FOREIGN KEY (code) REFERENCES redeem_codes(code)
    );
    
    CREATE TABLE IF NOT EXISTS welcome_settings (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        emoji TEXT DEFAULT '❤️',
        caption TEXT DEFAULT 'ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ʙᴏᴛ!',
        image_file_id TEXT,
        video_file_id TEXT,
        bot_dp_file_id TEXT,
        first_time_sticker TEXT,
        is_default INTEGER DEFAULT 1
    );
    
    CREATE TABLE IF NOT EXISTS logs (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        user_id INTEGER,
        action TEXT,
        details TEXT,
        timestamp TEXT
    );
    
    CREATE TABLE IF NOT EXISTS admins (
        user_id INTEGER PRIMARY KEY,
        added_by INTEGER,
        added_date TEXT,
        is_owner INTEGER DEFAULT 0
    );

    CREATE TABLE IF NOT EXISTS feature_costs (
        feature_key TEXT PRIMARY KEY,
        cost INTEGER DEFAULT 1
    );

    CREATE TABLE IF NOT EXISTS feature_maintenance (
        feature_key TEXT PRIMARY KEY,
        is_under_maintenance INTEGER DEFAULT 0,
        reason TEXT DEFAULT '',
        set_by INTEGER DEFAULT 0,
        set_at TEXT DEFAULT ''
    );
    
    CREATE TABLE IF NOT EXISTS force_join_channels (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        link TEXT UNIQUE,
        username TEXT,
        added_by INTEGER,
        added_date TEXT,
        channel_type TEXT DEFAULT 'channel'
    );
    
    CREATE TABLE IF NOT EXISTS bot_groups (
        group_id INTEGER PRIMARY KEY,
        group_title TEXT,
        number_info_enabled INTEGER DEFAULT 1,
        userid_info_enabled INTEGER DEFAULT 1,
        username_info_enabled INTEGER DEFAULT 1,
        aadhar_info_enabled INTEGER DEFAULT 1,
        instagram_info_enabled INTEGER DEFAULT 1,
        ifsc_info_enabled INTEGER DEFAULT 1,
        vehicle_info_enabled INTEGER DEFAULT 1,
        welcome_enabled INTEGER DEFAULT 1,
        welcome_message TEXT DEFAULT '🎉 𝗪𝗲𝗹𝗰𝗼𝗺𝗲 {name}!\n👥 {group}\n\n📅 {date}  🕐 {time}\n🌍 {language}\n📜 {rules}\n\n🚀 𝗘𝗻𝗷𝗼𝘆 𝘆𝗼𝘂𝗿 𝘀𝘁𝗮𝘆! 🎊',
        welcome_rules TEXT DEFAULT '',
        added_date TEXT,
        last_active TEXT
    );
''')
    conn.commit()

    # Migration: add missing columns
    try:
        c.execute("SELECT last_active FROM users LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE users ADD COLUMN last_active TEXT")
        conn.commit()
        print("✅ Added last_active column to users")

    try:
        c.execute("SELECT is_active FROM redeem_codes LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE redeem_codes ADD COLUMN is_active INTEGER DEFAULT 1")
        conn.commit()
        print("✅ Added is_active column to redeem_codes")

    for _col, _default in [
        ("goodbye_enabled", "1"),
        ("goodbye_message", "NULL"),  # ✅ BUG FIX: Default NULL - SQL ALTER mein string default crash karta tha
        ("welcome_photo_file_id", "NULL"),
        ("gst_info_enabled", "1"),
        ("email_info_enabled", "1"),
        ("pan_info_enabled", "1"),
        ("pak_num_info_enabled", "1"),
        ("ff_info_enabled", "1"),
        ("pincode_info_enabled", "1"),
        ("hitek_info_enabled", "1"),
        ("tg_bomber_enabled", "1"),
        ("bomber_enabled", "1"),
        ("free_info_mode", "0"),
    ]:
        try:
            c.execute(f"SELECT {_col} FROM bot_groups LIMIT 1")
        except sqlite3.OperationalError:
            c.execute(f"ALTER TABLE bot_groups ADD COLUMN {_col} INTEGER DEFAULT {_default}")
            conn.commit()
            print(f"✅ Added {_col} column to bot_groups")

    try:
        c.execute("SELECT money FROM users LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE users ADD COLUMN money INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Added money column to users")

    try:
        c.execute("SELECT clone_bots FROM users LIMIT 1")
    except sqlite3.OperationalError:
        c.execute("ALTER TABLE users ADD COLUMN clone_bots INTEGER DEFAULT 0")
        conn.commit()
        print("✅ Added clone_bots column to users")

    # Clone bots table
    try:
        c.execute("""
            CREATE TABLE IF NOT EXISTS clone_bots (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                token TEXT UNIQUE,
                status TEXT DEFAULT 'pending',
                requested_at TEXT,
                approved_at TEXT,
                is_manually_stopped INTEGER DEFAULT 0
            )
        """)
        # Add is_manually_stopped column if missing
        try:
            c.execute("SELECT is_manually_stopped FROM clone_bots LIMIT 1")
        except Exception:
            c.execute("ALTER TABLE clone_bots ADD COLUMN is_manually_stopped INTEGER DEFAULT 0")
            conn.commit()
        # Add bomber_history table
        c.execute("""
            CREATE TABLE IF NOT EXISTS bomber_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                target_number TEXT,
                sms_sent INTEGER DEFAULT 0,
                calls_sent INTEGER DEFAULT 0,
                status TEXT DEFAULT 'running',
                started_at TEXT,
                stopped_at TEXT
            )
        """)
        conn.commit()
    except Exception as e:
        print(f"⚠️ clone_bots table: {e}")

    # ── Clone tables ──
    try:
        c.execute("CREATE TABLE IF NOT EXISTS clone_admins (id INTEGER PRIMARY KEY AUTOINCREMENT, clone_token TEXT, admin_user_id INTEGER, added_by INTEGER, added_date TEXT, UNIQUE(clone_token, admin_user_id))")
        c.execute("CREATE TABLE IF NOT EXISTS clone_credits (id INTEGER PRIMARY KEY AUTOINCREMENT, clone_token TEXT, user_id INTEGER, credits INTEGER DEFAULT 0, UNIQUE(clone_token, user_id))")
        c.execute("CREATE TABLE IF NOT EXISTS clone_force_join (id INTEGER PRIMARY KEY AUTOINCREMENT, clone_token TEXT, link TEXT, username TEXT, channel_type TEXT DEFAULT 'channel', added_by INTEGER, added_date TEXT, UNIQUE(clone_token, link))")
        # ✅ NEW: Clone-specific users table — separate from main bot users
        c.execute("""CREATE TABLE IF NOT EXISTS clone_users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clone_token TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            username TEXT DEFAULT '',
            first_name TEXT DEFAULT '',
            join_date TEXT,
            referrer INTEGER,
            credits INTEGER DEFAULT 10,
            is_blocked INTEGER DEFAULT 0,
            is_premium INTEGER DEFAULT 0,
            premium_until TEXT,
            total_searches INTEGER DEFAULT 0,
            last_active TEXT,
            UNIQUE(clone_token, user_id)
        )""")
        # ✅ NEW: Clone-specific daily claims
        c.execute("""CREATE TABLE IF NOT EXISTS clone_daily_claims (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clone_token TEXT NOT NULL,
            user_id INTEGER NOT NULL,
            claim_date TEXT NOT NULL,
            UNIQUE(clone_token, user_id, claim_date)
        )""")
        # ✅ NEW: Clone-specific referrals
        c.execute("""CREATE TABLE IF NOT EXISTS clone_referrals (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clone_token TEXT NOT NULL,
            referrer INTEGER,
            referred INTEGER,
            date TEXT
        )""")
        # ✅ NEW: Clone-specific search history
        c.execute("""CREATE TABLE IF NOT EXISTS clone_search_history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            clone_token TEXT NOT NULL,
            user_id INTEGER,
            search_type TEXT,
            query TEXT,
            search_date TEXT,
            result TEXT
        )""")
        conn.commit()
    except Exception as e:
        print(f"⚠️ clone tables: {e}")

    # ── API Keys Tables ── ✅ NEW: User API generation feature
    try:
        c.execute("""CREATE TABLE IF NOT EXISTS user_api_keys (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            api_key TEXT UNIQUE NOT NULL,
            feature_key TEXT NOT NULL,
            created_at TEXT NOT NULL,
            expires_at TEXT NOT NULL,
            days INTEGER DEFAULT 1,
            credits_used INTEGER DEFAULT 0,
            is_active INTEGER DEFAULT 1,
            total_calls INTEGER DEFAULT 0,
            last_used TEXT
        )""")
        c.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_uid ON user_api_keys(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_api_keys_key ON user_api_keys(api_key)")
        c.execute("""CREATE TABLE IF NOT EXISTS api_pricing (
            feature_key TEXT NOT NULL,
            days INTEGER NOT NULL,
            credits INTEGER NOT NULL,
            is_enabled INTEGER DEFAULT 1,
            PRIMARY KEY (feature_key, days)
        )""")
        conn.commit()
        print("✅ API tables ready")
    except Exception as e:
        print(f"⚠️ API tables: {e}")

    # Add owner as admin if not exists
    try:
        c.execute("INSERT OR IGNORE INTO admins (user_id, added_by, added_date, is_owner) VALUES (?, ?, ?, ?)",
                  (OWNER_ID, OWNER_ID, datetime.now().strftime("%Y-%m-%d %H:%M:%S"), 1))
        conn.commit()
    except Exception:
        pass

    try:
        c.execute("""INSERT OR IGNORE INTO users
                     (user_id, username, first_name, join_date, referrer, credits, last_active)
                     VALUES (?, ?, ?, ?, ?, ?, ?)""",
                  (OWNER_ID, 'owner', 'Bot Owner',
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                   None, 0,
                   datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
        conn.commit()
    except Exception:
        pass

    try:
        conn.execute("PRAGMA wal_checkpoint(FULL)")
        conn.execute("PRAGMA optimize")
        conn.commit()
        conn.execute("VACUUM")
    except Exception:
        pass

    # Initialize welcome settings
    try:
        c.execute("SELECT COUNT(*) FROM welcome_settings")
        if c.fetchone()[0] == 0:
            c.execute("INSERT INTO welcome_settings (emoji, caption) VALUES (?, ?)",
                      ('❤️', 'ᴡᴇʟᴄᴏᴍᴇ ᴛᴏ ɪɴꜰᴏʀᴍᴀᴛɪᴏɴ ʙᴏᴛ!'))
            conn.commit()
    except Exception:
        pass

    # Migration: allow NULL username in force_join_channels
    try:
        c.execute("PRAGMA table_info(force_join_channels)")
        columns = c.fetchall()
        for col in columns:
            if col[1] == 'username' and col[3] == 1:
                c.execute("ALTER TABLE force_join_channels RENAME TO force_join_channels_old")
                c.execute('''CREATE TABLE force_join_channels (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    link TEXT UNIQUE, username TEXT,
                    added_by INTEGER, added_date TEXT)''')
                c.execute('''INSERT INTO force_join_channels (id, link, username, added_by, added_date)
                    SELECT id, link, username, added_by, added_date FROM force_join_channels_old''')
                c.execute("DROP TABLE force_join_channels_old")
                conn.commit()
                print("✅ force_join_channels table updated")
                break
    except Exception as e:
        print(f"⚠️ Migration error (ignored): {e}")

    # ✅ Add performance indexes if not exist
    try:
        c.execute("CREATE INDEX IF NOT EXISTS idx_users_uid ON users(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_search_uid ON search_history(user_id)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_daily_uid_date ON daily_claims(user_id, claim_date)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_redeem_code ON redeem_codes(code)")
        c.execute("CREATE INDEX IF NOT EXISTS idx_admins_uid ON admins(user_id)")
        conn.commit()
    except Exception: pass

    # Migration: add channel_type column if missing (bot_link feature)
    try:
        c.execute("PRAGMA table_info(force_join_channels)")
        cols = [col[1] for col in c.fetchall()]
        if 'channel_type' not in cols:
            c.execute("ALTER TABLE force_join_channels ADD COLUMN channel_type TEXT DEFAULT 'channel'")
            conn.commit()
            print("✅ force_join_channels: channel_type column added")
    except Exception as e:
        print(f"⚠️ channel_type migration error (ignored): {e}")

    print("✅ DB initialized successfully")


init_db()


# ✅ Flask already started at top of file (before DB restore) — port 10000 already bound
# web_thread removed to avoid double-start
reload_feature_costs()
reload_api_pricing()  # ✅ NEW: API pricing cache load karo
# This is called here because _ensure_group_settings_columns is defined later in the file
# It will run after init_db() but the flag prevents re-running


# Load channels on startup (2nd call - ensures fresh load after migrations)
load_channels_from_db()


# This ensures bot_groups table has all required columns before any group message arrives
try:
    _ensure_group_settings_columns()
    print("✅ Group settings columns verified")
except Exception as _gsc_err:
    print(f"⚠️ group settings columns: {_gsc_err}")
