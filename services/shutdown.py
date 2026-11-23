


# ✅ RENDER SHUTDOWN BACKUP: SIGTERM intercept karo
# Render deploy ke waqt pehle SIGTERM bhejta hai — hum data save karte hain
import signal as _signal
def _graceful_shutdown(signum, frame):
    """SIGTERM handler — backup all data to GitHub before exit."""
    import sys, base64 as _b64, urllib.request as _ur, json as _js
    print("⚠️ SIGTERM — backup shuru...")

    _token = os.environ.get("GH_TOKEN", "").strip()
    _repo  = os.environ.get("GH_REPO", "").strip()
    _path  = os.environ.get("GH_DB_PATH", "database.db")
    for _p in ("https://github.com/", "github.com/"):
        if _repo.startswith(_p): _repo = _repo[len(_p):].strip("/")

    if not (_token and _repo and os.path.exists('bot.db') and os.path.getsize('bot.db') > 4096):
        print("⚠️ Backup skip"); sys.exit(0)

    try:
        _wal_checkpoint()
        print("  ✅ WAL flush done")
    except Exception as e:
        print(f"  ⚠️ WAL: {e}")

    _hdrs = {
        "Authorization": f"Bearer {_token}",
        "Accept": "application/vnd.github+json",
        "Content-Type": "application/json",
        "X-GitHub-Api-Version": "2022-11-28"
    }

    def _upload(fpath, data_b64, msg):
        _api = f"https://api.github.com/repos/{_repo}/contents/{fpath}"
        _sha = None
        try:
            _rg = _ur.Request(_api, headers=_hdrs, method='GET')
            with _ur.urlopen(_rg, timeout=10) as _r: _sha = _js.loads(_r.read()).get('sha')
        except Exception: pass
        _pl = {"message": msg, "content": data_b64}
        if _sha: _pl["sha"] = _sha
        for _att in range(3):
            try:
                _rp = _ur.Request(_api, data=_js.dumps(_pl).encode(), headers=_hdrs, method='PUT')
                with _ur.urlopen(_rp, timeout=25) as _r2:
                    if _r2.status in (200, 201): return True
            except Exception as _e:
                if '409' in str(_e) or 'Conflict' in str(_e):
                    try:
                        _rg2 = _ur.Request(_api, headers=_hdrs, method='GET')
                        with _ur.urlopen(_rg2, timeout=10) as _rr: _pl["sha"] = _js.loads(_rr.read()).get('sha')
                    except Exception: pass
                time.sleep(2)
        return False

    _ts = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    _ok = False

    # Upload bot.db
    try:
        with open('bot.db', 'rb') as _f: _db = _f.read()
        _ok = _upload(_path, _b64.b64encode(_db).decode(), f"shutdown backup {_ts} [skip ci]")
        print(f"  {'✅' if _ok else '⚠️'} database.db {len(_db)//1024}KB {'OK' if _ok else 'FAILED'}")
    except Exception as e:
        print(f"  ❌ DB upload: {e}")

    # Retry if failed
    if not _ok:
        print("  Retry...")
        time.sleep(2)
        try:
            with open('bot.db', 'rb') as _f: _db2 = _f.read()
            _ok = _upload(_path, _b64.b64encode(_db2).decode(), f"shutdown retry {_ts} [skip ci]")
            print(f"  {'✅ Retry OK' if _ok else '❌ Retry fail'}")
        except Exception as _re: print(f"  ❌ {_re}")

    # Upload JSON backup
    try:
        _jpath = _path.replace('.db', '_backup.json') if '.db' in _path else "backup_data.json"
        _jlc = sqlite3.connect('bot.db', timeout=5)
        _jlc.row_factory = sqlite3.Row
        _jc = _jlc.cursor()

        def _qa(tbl):
            try:
                _jc.execute(f"SELECT * FROM {tbl}")
                _cols = [d[0] for d in _jc.description]
                return [dict(zip(_cols, r)) for r in _jc.fetchall()]
            except Exception: return []

        _jdata = {
            "backup_meta": {"version": "3.1", "created_at": _ts},
            "main_bot": {
                "users": _qa("users"), "admins": _qa("admins"),
                "force_join_channels": _qa("force_join_channels"),
                "bot_groups": _qa("bot_groups"), "redeem_codes": _qa("redeem_codes"),
                "redeemed_users": _qa("redeemed_users"), "feature_costs": _qa("feature_costs"),
                "feature_maintenance": _qa("feature_maintenance"),
                "daily_claims": _qa("daily_claims"), "welcome_settings": _qa("welcome_settings"),
                "referrals": _qa("referrals"), "search_history": _qa("search_history"),
                "bomber_history": _qa("bomber_history"), "logs": _qa("logs"),
            },
            "clone_bots": {
                "bots": _qa("clone_bots"), "admins": _qa("clone_admins"),
                "force_join": _qa("clone_force_join"), "credits": _qa("clone_credits"),
            },
            "clone_user_data": {},
        }
        try:
            _jc.execute("SELECT DISTINCT clone_token FROM clone_users")
            for (_ctok,) in _jc.fetchall():
                _ck = _ctok[:8] + "..."
                def _qc(tbl, tok=_ctok):
                    try:
                        _jc.execute(f"SELECT * FROM {tbl} WHERE clone_token=?", (tok,))
                        _cols = [d[0] for d in _jc.description]
                        return [dict(zip(_cols, r)) for r in _jc.fetchall()]
                    except Exception: return []
                _jdata["clone_user_data"][_ck] = {
                    "users": _qc("clone_users"), "daily_claims": _qc("clone_daily_claims"),
                    "referrals": _qc("clone_referrals"), "search_history": _qc("clone_search_history"),
                }
        except Exception: pass
        _jlc.close()
        _jstr = _js.dumps(_jdata, ensure_ascii=False, indent=2, default=str)
        _jok = _upload(_jpath, _b64.b64encode(_jstr.encode()).decode(), f"shutdown JSON {_ts} [skip ci]")
        print(f"  {'✅' if _jok else '⚠️'} {_jpath} {len(_jstr)//1024}KB")
    except Exception as e:
        print(f"  ⚠️ JSON backup: {e}")

    print(f"{'✅' if _ok else '❌'} Shutdown {'SUCCESS' if _ok else 'FAILED'}")
    sys.exit(0)
_signal.signal(_signal.SIGTERM, _graceful_shutdown)
_signal.signal(_signal.SIGINT,  _graceful_shutdown)
print("✅ SIGTERM/SIGINT handler registered — safe shutdown backup enabled")