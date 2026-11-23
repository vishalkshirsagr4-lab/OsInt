


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