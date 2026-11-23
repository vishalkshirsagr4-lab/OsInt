

@app.route('/health')
def health():
    """Health check."""
    try:
        db_size = os.path.getsize('bot.db') // 1024 if os.path.exists('bot.db') else 0
        gh_ok = bool(os.environ.get("GH_TOKEN") and os.environ.get("GH_REPO"))
        users = admins = clone_users = 0
        try:
            _hc = sqlite3.connect('bot.db', timeout=5)
            users = _hc.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            admins = _hc.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
            try: clone_users = _hc.execute("SELECT COUNT(*) FROM clone_users").fetchone()[0]
            except Exception: pass
            _hc.close()
        except Exception: pass
        return f"OK | DB:{db_size}KB | GH:{'✓' if gh_ok else '✗'} | Users:{users} | Admins:{admins} | CloneUsers:{clone_users}", 200
    except Exception:
        return "OK", 200