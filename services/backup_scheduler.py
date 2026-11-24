

def schedule_db_backup(interval_minutes: int = 2) -> None:
    """Periodic GitHub backup every N minutes."""
    def _loop():
        time.sleep(30)  # first backup 30s after start
        while True:
            try:
                if os.path.exists('bot.db') and os.path.getsize('bot.db') >= 4096:
                    _tmp = sqlite3.connect('bot.db', timeout=5)
                    try: _cu = _tmp.execute("SELECT COUNT(*) FROM clone_users").fetchone()[0]
                    except Exception: _cu = 0
                    finally: _tmp.close()
                    result = github_upload_db()
                    print(f"{'✅' if result else '❌'} [auto-backup] done (clone_users: {_cu})")
                else:
                    print("⚠️ [auto-backup] SKIP: DB missing/too small")
            except Exception as e:
                print(f"⚠️ [auto-backup] {e}")
            time.sleep(interval_minutes * 60)
    t = threading.Thread(target=_loop, daemon=True, name="auto_backup")
    t.start()
    print(f"✅ Auto-backup started (every {interval_minutes} min)")


_backup_timer = None
_last_backup_time = 0.0


def trigger_backup_soon() -> None:
    """Debounced backup — collapses rapid writes into one upload."""
    global _backup_timer
    if not GITHUB_TOKEN or not GITHUB_REPO:
        return

    def _safe_backup():
        global _last_backup_time, _backup_timer
        try:
            elapsed = time.time() - _last_backup_time
            if elapsed < _BACKUP_MIN_INTERVAL:
                wait = _BACKUP_MIN_INTERVAL - elapsed
                _backup_timer = threading.Timer(wait, _safe_backup)
                _backup_timer.daemon = True
                _backup_timer.start()
                return
            if not os.path.exists('bot.db') or os.path.getsize('bot.db') < 4096:
                return
            if github_upload_db():
                _last_backup_time = time.time()
        except Exception as _e:
            print(f"⚠️ [trigger_backup] {_e}")

    if _backup_timer is not None:
        try: _backup_timer.cancel()
        except Exception: pass
    _backup_timer = threading.Timer(5.0, _safe_backup)
    _backup_timer.daemon = True
    _backup_timer.start()