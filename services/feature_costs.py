


# ── Feature Credit Costs (Admin can change at runtime) ──
# Feature costs loaded from DB, fallback to defaults
from dbm import sqlite3


_FEATURE_COST_DEFAULTS = {
    'mobile_number': 1, 'username': 1, 'userid': 1, 'aadhar': 1,
    'instagram': 1, 'ifsc': 1, 'vehicle': 1, 'gst': 1,
    'email': 1, 'pan': 1, 'pak_num': 1, 'pincode': 1, 'ff': 1,
    'hitek_num': 2, 'hitek_full': 2,
}


def _load_feature_costs():
    """Load feature costs from DB, fallback to defaults."""
    try:
        _conn = sqlite3.connect('bot.db', timeout=15)
        _c = _conn.cursor()
        _c.execute("SELECT feature_key, cost FROM feature_costs")
        rows = _c.fetchall()
        _conn.close()
        result = dict(_FEATURE_COST_DEFAULTS)
        for key, cost in rows:
            result[key] = cost
        return result
    except Exception:
        return dict(_FEATURE_COST_DEFAULTS)

def _save_feature_cost(key, cost):
    """Persist a single feature cost to DB."""
    try:
        _conn = sqlite3.connect('bot.db', timeout=15)
        _c = _conn.cursor()
        _c.execute("INSERT OR REPLACE INTO feature_costs (feature_key, cost) VALUES (?, ?)", (key, cost))
        _conn.commit()
        _conn.close()
    except Exception as e:
        print(f"Error saving feature cost: {e}")


# init_db() ke baad reload_feature_costs() call hogi jab DB ready ho
FEATURE_COSTS = dict(_FEATURE_COST_DEFAULTS)

def reload_feature_costs():
    """init_db() ke baad call karo — DB se actual costs load karta hai."""
    global FEATURE_COSTS
    FEATURE_COSTS = _load_feature_costs()