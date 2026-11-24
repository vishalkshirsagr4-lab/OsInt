


FORCE_JOIN_LINKS: list = []
FORCE_JOIN_USERNAMES: list = []

# USER STATE & BYPASS MODE TRACKING
user_state = {}           # For command states
hist_pages: dict = {}     # uid -> history sub-menu state ('main','search','bomber','stats')
# user_pages — tracks current keyboard page per user
user_pages: dict = {}  # ✅ BUG FIX: Was removed by mistake but is actively used
admin_page = {}           # Per-user admin page tracking (thread-safe)
admin_selected_group: dict = {}  # Track which group admin has selected for group welcome settings


_confirm_pending: dict = {}

hist_search_page: dict = {} # uid -> current search page number

result_pages: dict = {}   # uid -> pagination state

def _cleanup_result_pages():
    import time as _t
    now = _t.time()
    stale = [k for k, v in list(result_pages.items()) if isinstance(v , dict) and now - v.get('ts',now)>1800]
    for k in stale:
        result_pages.pop(k,None)


# Load channels from database
_channels_lock = threading.Lock()  # ✅ FIX: thread-safe channel updates

_admin_cache: dict = {}        # uid -> bool
_admin_cache_ts: dict = {}     # uid -> timestamp


_grp_settings_migrated = False