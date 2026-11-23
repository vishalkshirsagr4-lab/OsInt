

# ── API Pricing Defaults: {days: credits} ──
_API_PLAN_DEFAULTS = {0.25: 1, 0.5: 1, 1: 2, 3: 5, 7: 10, 30: 30}  # hours + days
API_VALIDITY_PLANS = [0.25, 0.5, 1, 3, 7, 30]  # 0.25=6hr, 0.5=12hr, rest=days
API_PRICING_CACHE: dict = {}  # {(feature_key, days): {'credits': int, 'enabled': bool}}


def _load_api_pricing():
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        rows = lc.execute("SELECT feature_key, days, credits, is_enabled FROM api_pricing").fetchall()
        lc.close()
        result = {}
        for fkey, days, creds, enabled in rows:
            result[(fkey, days)] = {'credits': creds, 'enabled': bool(enabled)}
        return result
    except Exception:
        return {}

def reload_api_pricing():
    """API pricing cache refresh karo."""
    global API_PRICING_CACHE
    try:
        API_PRICING_CACHE = _load_api_pricing()
    except Exception as e:
        print(f"[reload_api_pricing] {e}")
        API_PRICING_CACHE = {}

def _save_api_pricing(feature_key: str, days: int, credits: int, is_enabled: int = 1):
    try:
        lc = sqlite3.connect('bot.db', timeout=15)
        lc.execute("INSERT OR REPLACE INTO api_pricing (feature_key, days, credits, is_enabled) VALUES (?, ?, ?, ?)",
                   (feature_key, days, credits, is_enabled))
        lc.commit()
        lc.close()
        reload_api_pricing()
    except Exception as e:
        print(f"[api_pricing] save error: {e}")



def get_api_credit_cost(feature_key: str, days: int) -> int:
    """Feature + days ke liye credit cost return karo."""
    try:
        cached = API_PRICING_CACHE.get((feature_key, days))
        if cached and isinstance(cached, dict):
            return cached.get('credits', _API_PLAN_DEFAULTS.get(days, days))
    except Exception:
        pass
    return _API_PLAN_DEFAULTS.get(days, days)

def is_api_feature_enabled(feature_key: str) -> bool:
    for (fk, d), info in API_PRICING_CACHE.items():
        if fk == feature_key and info.get('enabled'):
            return True
    # Default enabled if no DB entry
    return True