


def _generate_api_key() -> str:
    prefix = "OSINT"
    p1 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    p2 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=8))
    p3 = ''.join(random.choices(string.ascii_uppercase + string.digits, k=6))
    return f"{prefix}-{p1}-{p2}-{p3}"

def create_user_api_key(user_id: int, feature_key: str, days: int, credits_used: int) -> dict:
    try:
        now = datetime.now()
        # Support hours: 0.25=6hr, 0.5=12hr, else days
        if days < 1:
            expires = now + timedelta(hours=days * 24)
        else:
            expires = now + timedelta(days=days)
        api_key = _generate_api_key()
        created_str = now.strftime('%Y-%m-%d %H:%M:%S')
        expires_str = expires.strftime('%Y-%m-%d %H:%M:%S')
        for _ in range(5):
            lc = sqlite3.connect('bot.db', timeout=15)
            try:
                lc.execute(
                    "INSERT INTO user_api_keys (user_id, api_key, feature_key, created_at, expires_at, days, credits_used, is_active) VALUES (?, ?, ?, ?, ?, ?, ?, 1)",
                    (user_id, api_key, feature_key, created_str, expires_str, days, credits_used)
                )
                lc.commit()
                lc.close()
                return {'success': True, 'api_key': api_key, 'expires_at': expires_str}
            except sqlite3.IntegrityError:
                lc.close()
                api_key = _generate_api_key()
            except Exception as e:
                lc.close()
                return {'success': False, 'error': str(e)}
        return {'success': False, 'error': 'Key generation failed'}
    except Exception as e:
        return {'success': False, 'error': str(e)}

def get_user_api_keys(user_id: int) -> list:
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        rows = lc.execute(
            "SELECT api_key, feature_key, created_at, expires_at, days, credits_used, is_active, total_calls, last_used FROM user_api_keys WHERE user_id=? ORDER BY created_at DESC LIMIT 20",
            (user_id,)
        ).fetchall()
        lc.close()
        now = datetime.now()
        keys = []
        for row in rows:
            api_key, fkey, created, expires, days, credits_used, is_active, total_calls, last_used = row
            try:
                expired = datetime.strptime(expires, '%Y-%m-%d %H:%M:%S') < now
            except Exception:
                expired = False
            keys.append({
                'api_key': api_key, 'feature_key': fkey,
                'feature_label': globals().get('FEAT_DISPLAY_NAMES', {}).get(fkey, fkey.replace('_', ' ').title()),
                'created_at': created, 'expires_at': expires, 'days': days,
                'credits_used': credits_used, 'is_active': is_active and not expired,
                'expired': expired, 'total_calls': total_calls or 0,
                'last_used': last_used or 'Never',
            })
        return keys
    except Exception as e:
        print(f"[get_user_api_keys] {e}")
        return []

def revoke_api_key(user_id: int, api_key: str) -> bool:
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        lc.execute("UPDATE user_api_keys SET is_active=0 WHERE user_id=? AND api_key=?", (user_id, api_key))
        changed = lc.execute("SELECT changes()").fetchone()[0]
        lc.commit()
        lc.close()
        return changed > 0
    except Exception:
        return False

def validate_api_key(api_key: str) -> dict:
    if not api_key or not api_key.startswith("OSINT-"):
        return {'valid': False, 'error': 'Invalid API key format. Key must start with OSINT-'}
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        row = lc.execute(
            "SELECT user_id, feature_key, expires_at, is_active, total_calls FROM user_api_keys WHERE api_key=?",
            (api_key,)
        ).fetchone()
        if not row:
            lc.close()
            return {'valid': False, 'error': 'Invalid API key'}
        user_id, feature_key, expires_at, is_active, total_calls = row
        if not is_active:
            lc.close()
            return {'valid': False, 'error': 'API key is revoked'}
        try:
            if datetime.strptime(expires_at, '%Y-%m-%d %H:%M:%S') < datetime.now():
                lc.close()
                return {'valid': False, 'error': f'API key expired on {expires_at}'}
        except Exception:
            pass
        now_str = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        lc.execute("UPDATE user_api_keys SET total_calls=total_calls+1, last_used=? WHERE api_key=?", (now_str, api_key))
        lc.commit()
        lc.close()
        return {'valid': True, 'user_id': user_id, 'feature_key': feature_key, 'expires_at': expires_at}
    except Exception as e:
        return {'valid': False, 'error': str(e)}