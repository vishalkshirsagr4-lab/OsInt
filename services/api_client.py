


# ══════════════════════════════════════════════════════════
# ✅ UNIVERSAL API HELPER — All APIs use same shadow-osint base
# Response format: {"success": true/false, "data": {...} or [...], "message": "..."}
# ══════════════════════════════════════════════════════════
def _shadow_api(type_: str, query: str, extra_params: dict = None, timeout: int = 20) -> dict:
    """Universal caller for shadow-osint API. Returns normalized dict.
    Handles all possible response formats from the new unified API.
    """
    try:
        BASE = "https://shadow-osint.vercel.app"
        KEY  = "SH"
        if type_ == "instagram":
            url = f"{BASE}/?type=instagram&username={query}&key={KEY}"
        else:
            url = f"{BASE}/?type={type_}&query={query}&key={KEY}"
        if extra_params:
            import urllib.parse
            url += "&" + urllib.parse.urlencode(extra_params)
        print(f"[shadow_api] Calling: {url}")
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"}, timeout=timeout)
        print(f"[shadow_api:{type_}] HTTP {resp.status_code}")
        if resp.status_code != 200:
            return {"success": False, "msg": f"HTTP {resp.status_code}"}
        try:
            data = resp.json()
            print(f"[shadow_api:{type_}] Response keys: {list(data.keys()) if isinstance(data, dict) else type(data).__name__}")
        except Exception:
            return {"success": False, "msg": "Invalid JSON response"}

        # ── Explicit error check ──
        if isinstance(data, dict):
            if data.get("error") is True or str(data.get("status",'')).lower() in ('error','fail','false'):
                msg = data.get("message") or data.get("msg") or data.get("error") or "No data found"
                return {"success": False, "msg": str(msg)}

        # ── Success detection — very permissive ──
        ok = False
        if isinstance(data, dict):
            ok = bool(
                data.get("success") is True or
                data.get("success") == 1 or
                str(data.get("success","")).lower() == "true" or
                data.get("status") is True or
                data.get("status") == 1 or
                str(data.get("status","")).lower() in ("success","true","ok","1") or
                data.get("found") is True or
                # New API: has "result" key with data
                (data.get("result") and data.get("result") not in (None, [], {})) or
                # Has any meaningful non-meta key
                any(k not in ("success","status","error","message","msg","n","key","apikey","query","type")
                    for k in data.keys())
            )
        elif isinstance(data, list) and len(data) > 0:
            ok = True

        if not ok:
            msg = (data.get("message") or data.get("msg") or
                   data.get("error") or "No data found") if isinstance(data, dict) else "No data found"
            return {"success": False, "msg": str(msg)}

        return {"success": True, "_raw": data, "data": data.get("data") if isinstance(data, dict) else data}
    except requests.exceptions.Timeout:
        return {"success": False, "msg": "API timeout — dobara try karo"}
    except Exception as e:
        print(f"[shadow_api:{type_}] Error: {e}")
        return {"success": False, "msg": str(e)}