

# Pehle init_db() line 745 pe run hoti thi (module level) aur GitHub restore
# 14000+ lines baad hoti thi. Is beech koi bhi message aata to empty DB use hoti.
# Ab: pehle GitHub se asli DB download karo, PHIR tables initialize karo.

def _restore_db_from_github() -> bool:
    """
    ✅ SINGLE CLEAN DB RESTORE — runs at module load, BEFORE init_db().
    Render pe har deploy ke baad local bot.db wipe ho jaati hai.
    Ye function GitHub se real DB download karke restore karta hai.

    Returns True if restored, False if first deploy / error / not configured.
    """
    import base64 as _b64
    _token = os.environ.get("GH_TOKEN", "").strip()
    _repo  = os.environ.get("GH_REPO", "").strip()
    _path  = os.environ.get("GH_DB_PATH", "database.db")

    # Strip any full GitHub URL — only want "username/reponame"
    for _pfx in ("https://github.com/", "http://github.com/", "github.com/"):
        if _repo.startswith(_pfx):
            _repo = _repo[len(_pfx):].strip("/")

    if not _token or not _repo:
        print("⚠️ [DB-RESTORE] GH_TOKEN ya GH_REPO set nahi — GitHub restore skip")
        print("   Render > Environment Variables mein GH_TOKEN aur GH_REPO set karo!")
        return False

    print(f"🔄 [DB-RESTORE] GitHub se restore kar raha hun: {_repo}/{_path}")
    _hdrs = {
        "Authorization": f"Bearer {_token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
    }
    _api = f"https://api.github.com/repos/{_repo}/contents/{_path}"

    for _att in range(7):  # 7 retries × 5s = 35s max — Render cold start ke liye
        try:
            _r = requests.get(_api, headers=_hdrs, timeout=20)

            if _r.status_code == 401:
                print("❌ [DB-RESTORE] GH_TOKEN invalid ya expired!")
                print("   GitHub > Settings > Developer settings > Personal access tokens > Classic")
                print("   'repo' scope wala naya token banao aur Render mein GH_TOKEN update karo.")
                return False

            if _r.status_code == 404:
                print("ℹ️ [DB-RESTORE] GitHub pe backup file nahi mili.")
                print("   Pehla deploy hai? Bot chalane ke 60s baad automatic backup ho jaayega.")
                return False

            if _r.status_code == 403:
                print("❌ [DB-RESTORE] GitHub rate limit ya permission error!")
                time.sleep(10)
                continue

            if _r.status_code != 200:
                print(f"⚠️ [DB-RESTORE] GitHub HTTP {_r.status_code} — retry {_att+1}/7 (5s)...")
                time.sleep(5)
                continue

            _data = _r.json()
            _db_bytes = b""

            # GitHub returns content as base64 (small files) or download_url (large files)
            if _data.get("content"):
                _db_bytes = _b64.b64decode(_data["content"].replace("\n", ""))
            elif _data.get("download_url"):
                _r2 = requests.get(_data["download_url"], headers=_hdrs, timeout=60)
                if _r2.status_code == 200:
                    _db_bytes = _r2.content
                else:
                    print(f"⚠️ [DB-RESTORE] Download URL fail: {_r2.status_code} — retry...")
                    time.sleep(5)
                    continue
            else:
                print(f"⚠️ [DB-RESTORE] Response mein content ya download_url nahi — retry...")
                time.sleep(5)
                continue

            # Validate — must be at least a valid SQLite file (512 bytes min)
            if len(_db_bytes) < 512:
                print(f"⚠️ [DB-RESTORE] Backup file bahut chhoti hai ({len(_db_bytes)} bytes) — skip.")
                return False
            # Check SQLite magic bytes (first 16 bytes = "SQLite format 3")
            if not _db_bytes[:6] == b'SQLite':
                # Still try — might be valid
                print(f"⚠️ [DB-RESTORE] SQLite magic bytes missing — trying anyway ({len(_db_bytes)} bytes)")

            # Write bot.db
            with open('bot.db', 'wb') as _f:
                _f.write(_db_bytes)

            # Quick verify — check restored DB has real data
            try:
                import sqlite3 as _sv
                _vc2 = _sv.connect('bot.db', timeout=5)
                _a2 = _vc2.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
                _u2 = _vc2.execute("SELECT COUNT(*) FROM users").fetchone()[0]
                try: _cu2 = _vc2.execute("SELECT COUNT(*) FROM clone_users").fetchone()[0]
                except Exception: _cu2 = 0
                try: _cb2 = _vc2.execute("SELECT COUNT(*) FROM clone_bots WHERE status='approved'").fetchone()[0]
                except Exception: _cb2 = 0
                try:
                    _clone_tokens_list = [r[0] for r in _vc2.execute("SELECT DISTINCT clone_token FROM clone_users").fetchall()]
                except Exception: _clone_tokens_list = []
                _vc2.close()
                # ✅ STRICT: Reject restore if no admins (empty/corrupt backup)
                if _a2 == 0:
                    print(f"❌ [DB-RESTORE] REJECTED: Backup file mein 0 admins — ye empty/corrupt DB hai!")
                    print(f"   Fresh DB se start kar raha hun — apna data fir se setup karo.")
                    # Remove the bad file, start fresh
                    try: os.remove('bot.db')
                    except Exception: pass
                    return False
                print(f"✅ [DB-RESTORE] SUCCESS! {len(_db_bytes)//1024} KB restored")
                print(f"   📊 Main Bot: {_u2} users | {_a2} admins")
                print(f"   🤖 Clone Bots: {_cb2} approved | {_cu2} clone users | {len(_clone_tokens_list)} active clones")
            except Exception as _ve2:
                print(f"✅ [DB-RESTORE] SUCCESS! Restored {len(_db_bytes)//1024} KB (stats check failed: {_ve2})")
            return True

        except Exception as _e:
            print(f"❌ [DB-RESTORE] Attempt {_att+1}/7 error: {_e} — retry 5s...")
            time.sleep(5)

    print("❌ [DB-RESTORE] Sab 7 attempts fail — fresh/local DB se start kar raha hun.")
    return False



def _export_structured_json() -> dict:
    """Export all bot data as structured JSON for GitHub backup."""
    try:
        _wal_checkpoint()
        lc = sqlite3.connect('bot.db', timeout=15)
        lc.row_factory = sqlite3.Row
        _exp_c = lc.cursor()  # ✅ FIX: renamed from 'c' to avoid shadowing global cursor

        def _fetch(table):
            try:
                _exp_c.execute(f"SELECT * FROM {table}")
                cols = [d[0] for d in _exp_c.description]
                return [dict(zip(cols, row)) for row in _exp_c.fetchall()]
            except Exception: return []

        data = {
            "backup_meta": {"version": "3.1", "created_at": datetime.now().strftime("%Y-%m-%d %H:%M:%S")},
            "main_bot": {
                "users": _fetch("users"), "admins": _fetch("admins"),
                "force_join_channels": _fetch("force_join_channels"),
                "bot_groups": _fetch("bot_groups"), "redeem_codes": _fetch("redeem_codes"),
                "redeemed_users": _fetch("redeemed_users"), "feature_costs": _fetch("feature_costs"),
                "feature_maintenance": _fetch("feature_maintenance"),
                "daily_claims": _fetch("daily_claims"), "welcome_settings": _fetch("welcome_settings"),
                "referrals": _fetch("referrals"), "search_history": _fetch("search_history"),
                "bomber_history": _fetch("bomber_history"), "logs": _fetch("logs"),
            },
            "clone_bots": {
                "bots": _fetch("clone_bots"), "admins": _fetch("clone_admins"),
                "force_join": _fetch("clone_force_join"), "credits": _fetch("clone_credits"),
            },
            "clone_user_data": {},
        }

        try:
            _exp_c.execute("SELECT DISTINCT clone_token FROM clone_users")
            for (tok,) in _exp_c.fetchall():
                tok_key = tok[:8] + "..."
                def _fetch_clone(table, _tok=tok):
                    try:
                        _lc2 = sqlite3.connect('bot.db', timeout=10)
                        _lc2.row_factory = sqlite3.Row
                        _cur2 = _lc2.cursor()
                        _cur2.execute(f"SELECT * FROM {table} WHERE clone_token=?", (_tok,))
                        cols = [d[0] for d in _cur2.description]
                        result = [dict(zip(cols, row)) for row in _cur2.fetchall()]
                        _lc2.close()
                        return result
                    except Exception: return []
                data["clone_user_data"][tok_key] = {
                    "users": _fetch_clone("clone_users"),
                    "daily_claims": _fetch_clone("clone_daily_claims"),
                    "referrals": _fetch_clone("clone_referrals"),
                    "search_history": _fetch_clone("clone_search_history"),
                }
        except Exception: pass
        lc.close()

        data["backup_meta"]["stats"] = {
            "main_users": len(data["main_bot"]["users"]),
            "main_admins": len(data["main_bot"]["admins"]),
            "clone_bots": len(data["clone_bots"]["bots"]),
            "total_clone_users": sum(len(v["users"]) for v in data["clone_user_data"].values()),
        }
        return data
    except Exception as e:
        print(f"[export_json] {e}"); return {}


def github_upload_db() -> bool:
    """Upload bot.db + JSON backup to GitHub. Thread-safe."""
    import base64 as _b64
    if not _backup_lock.acquire(blocking=False):
        return False
    try:
        token = GITHUB_TOKEN.strip()
        repo  = _clean_repo(GITHUB_REPO)
        if not token or not repo:
            return False
        if not os.path.exists('bot.db') or os.path.getsize('bot.db') < 4096:
            return False

        # WAL flush — sab pending data bot.db mein likho
        try:
            _wc = sqlite3.connect('bot.db', timeout=10)
            _wc.execute("PRAGMA wal_checkpoint(TRUNCATE)")
            _wc.execute("PRAGMA optimize")
            _wc.commit()
            result = _wc.execute("PRAGMA wal_checkpoint(FULL)").fetchone()
            print(f"  [WAL] pages={result[1] if result else '?'} moved={result[2] if result else '?'}")
            _wc.close()
            time.sleep(0.3)
        except Exception as _we:
            print(f"  [WAL] {_we}")

        # Integrity check
        try:
            _vc = sqlite3.connect('bot.db', timeout=5)
            _a = _vc.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
            _u = _vc.execute("SELECT COUNT(*) FROM users").fetchone()[0]
            try: _cu = _vc.execute("SELECT COUNT(*) FROM clone_users").fetchone()[0]
            except Exception: _cu = 0
            try: _cb = _vc.execute("SELECT COUNT(*) FROM clone_bots").fetchone()[0]
            except Exception: _cb = 0
            _vc.close()
            if _a == 0: return False
            print(f"📊 [backup] {_u} users | {_a} admins | {_cu} clone users | {_cb} clone bots")
        except Exception as _ve:
            print(f"⚠️ [backup] DB check: {_ve}"); return False

        headers = {
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28"
        }
        repo_r = requests.get(f"https://api.github.com/repos/{repo}", headers=headers, timeout=10)
        if repo_r.status_code == 401: print("❌ [backup] GH_TOKEN invalid!"); return False
        if repo_r.status_code == 404: print(f"❌ [backup] Repo not found: {repo}"); return False
        if repo_r.status_code != 200: return False
        real_repo = repo_r.json().get("full_name", repo)

        success_count = 0
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        # Upload bot.db binary
        try:
            with open('bot.db', 'rb') as f: db_bytes = f.read()
            db_encoded = _b64.b64encode(db_bytes).decode()
            db_url = f"https://api.github.com/repos/{real_repo}/contents/{GITHUB_DB_PATH}"
            r = requests.get(db_url, headers=headers, timeout=15)
            db_sha = r.json().get("sha") if r.status_code == 200 else None
            db_payload = {"message": f"backup {timestamp} — {_u} users, {_cu} clone users [skip ci]",
                          "content": db_encoded}
            if db_sha: db_payload["sha"] = db_sha
            for _att in range(3):
                r2 = requests.put(db_url, headers=headers, json=db_payload, timeout=60)
                if r2.status_code in (200, 201):
                    print(f"✅ [backup] database.db {len(db_bytes)//1024}KB uploaded")
                    success_count += 1; break
                elif r2.status_code == 409:
                    r3 = requests.get(db_url, headers=headers, timeout=10)
                    if r3.status_code == 200: db_payload["sha"] = r3.json().get("sha")
                    time.sleep(2)
                else:
                    time.sleep(3)
        except Exception as e:
            print(f"❌ [backup] DB upload: {e}")

        # Upload JSON backup
        try:
            json_data = _export_structured_json()
            if json_data:
                json_str = json.dumps(json_data, ensure_ascii=False, indent=2, default=str)
                json_encoded = _b64.b64encode(json_str.encode()).decode()
                json_path = GITHUB_DB_PATH.replace('.db', '_backup.json') if '.db' in GITHUB_DB_PATH else "backup_data.json"
                json_url = f"https://api.github.com/repos/{real_repo}/contents/{json_path}"
                rj = requests.get(json_url, headers=headers, timeout=10)
                json_sha = rj.json().get("sha") if rj.status_code == 200 else None
                json_payload = {"message": f"JSON backup {timestamp} [skip ci]", "content": json_encoded}
                if json_sha: json_payload["sha"] = json_sha
                for _att in range(3):
                    rj2 = requests.put(json_url, headers=headers, json=json_payload, timeout=60)
                    if rj2.status_code in (200, 201):
                        print(f"✅ [backup] {json_path} {len(json_str)//1024}KB uploaded")
                        success_count += 1; break
                    elif rj2.status_code == 409:
                        rj3 = requests.get(json_url, headers=headers, timeout=10)
                        if rj3.status_code == 200: json_payload["sha"] = rj3.json().get("sha")
                        time.sleep(2)
                    else:
                        time.sleep(3)
        except Exception as e:
            print(f"⚠️ [backup] JSON: {e}")

        return success_count >= 1
    except Exception as e:
        print(f"❌ [backup] Error: {e}"); return False
    finally:
        _backup_lock.release()


def github_restore_db() -> bool:
    """Download database.db from GitHub and restore as bot.db.
    
    Primary restore: database.db (binary SQLite)
    After restore: shows structured stats from backup_data.json if available.
    Returns True on success.
    """
    import base64 as _b64
    token = GITHUB_TOKEN.strip()
    repo  = _clean_repo(GITHUB_REPO)
    if not token or not repo:
        print("⚠️ GitHub restore: token/repo not set")
        return False
    
    headers = {
        "Authorization": f"Bearer {token}",
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28"
    }
    
    # ── Step 1: Restore binary database.db ──────────────────────
    try:
        api_url = f"https://api.github.com/repos/{repo}/contents/{GITHUB_DB_PATH}"
        r = requests.get(api_url, headers=headers, timeout=15)
        if r.status_code == 404:
            print("⚠️ GitHub restore: database.db not found (do a manual backup first)")
            return False
        if r.status_code != 200:
            print(f"❌ GitHub restore failed: {r.status_code} — {r.text[:200]}")
            return False
        data = r.json()
        if "content" in data and data["content"]:
            db_bytes = _b64.b64decode(data["content"].replace("\n",""))
        elif "download_url" in data and data["download_url"]:
            r2 = requests.get(data["download_url"], timeout=60)
            if r2.status_code != 200:
                print(f"❌ Download URL failed: {r2.status_code}")
                return False
            db_bytes = r2.content
        else:
            print("❌ GitHub restore: no content in response")
            return False
        
        if len(db_bytes) < 4096:
            print(f"⚠️ DB too small ({len(db_bytes)} bytes) — placeholder, skip restore")
            return False
        
        with open('bot.db', 'wb') as f:
            f.write(db_bytes)
        print(f"✅ database.db restored ({len(db_bytes)//1024} KB)")
        
    except Exception as e:
        print(f"❌ GitHub restore error: {e}")
        # Retry once
        try:
            time.sleep(3)
            r_retry = requests.get(api_url, headers=headers, timeout=30)
            if r_retry.status_code == 200:
                d2 = r_retry.json()
                url2 = d2.get("download_url")
                if url2:
                    r3 = requests.get(url2, timeout=60)
                    if len(r3.content) >= 4096:
                        with open('bot.db', 'wb') as f:
                            f.write(r3.content)
                        print(f"✅ DB restored (retry) — {len(r3.content)//1024} KB")
                    else: return False
                else: return False
            else: return False
        except Exception as e2:
            print(f"❌ Retry failed: {e2}")
            return False
    
    # ── Step 2: Quick verify restored DB ────────────────────────
    try:
        _vc = sqlite3.connect('bot.db', timeout=5)
        _u2 = _vc.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        _a2 = _vc.execute("SELECT COUNT(*) FROM admins").fetchone()[0]
        try: _cu2 = _vc.execute("SELECT COUNT(*) FROM clone_users").fetchone()[0]
        except Exception: _cu2 = 0
        try: _cb2 = _vc.execute("SELECT COUNT(*) FROM clone_bots").fetchone()[0]
        except Exception: _cb2 = 0
        _vc.close()
        print(f"📊 Restored: {_u2} main users | {_a2} admins | {_cu2} clone users | {_cb2} clone bots")
    except Exception as ve:
        print(f"⚠️ Post-restore verify failed: {ve}")
    
    # ── Step 3: Try to also read JSON backup for extra info ──────
    try:
        json_path = GITHUB_DB_PATH.replace('.db', '_backup.json')
        if json_path == GITHUB_DB_PATH: json_path = "backup_data.json"
        json_api = f"https://api.github.com/repos/{repo}/contents/{json_path}"
        rj = requests.get(json_api, headers=headers, timeout=10)
        if rj.status_code == 200:
            jdata = rj.json()
            if jdata.get("content"):
                jstr = _b64.b64decode(jdata["content"].replace("\n","")).decode('utf-8')
                jobj = json.loads(jstr)
                meta = jobj.get("backup_meta", {})
                stats = meta.get("stats", {})
                print(f"📋 JSON backup info: created={meta.get('created_at','?')} | "
                      f"main_users={stats.get('main_users','?')} | "
                      f"clone_bots={stats.get('clone_bots','?')} | "
                      f"clone_users={stats.get('total_clone_users','?')}")
    except Exception:
        pass  # JSON backup is optional — DB restore already done
    
    return True

_backup_lock = threading.Lock()