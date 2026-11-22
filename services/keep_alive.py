def _keep_alive():
    """Ping self every 10 min — prevents Render free tier sleep."""
    import urllib.request as _ka_ur
    _url = os.environ.get("RENDER_EXTERNAL_URL", "").strip()
    if not _url:
        _svc = os.environ.get("RENDER_SERVICE_NAME", "").strip()
        if _svc: _url = f"https://{_svc}.onrender.com"
    if not _url:
        print("⚠️ [keep-alive] Set RENDER_EXTERNAL_URL in Render env vars")
        return
    print(f"✅ [keep-alive] Pinging {_url} every 10 min")
    while True:
        try:
            time.sleep(600)
            with _ka_ur.urlopen(_ka_ur.Request(f"{_url}/health", method='GET'), timeout=15) as _r:
                print(f"✅ [keep-alive] OK ({_r.status})")
        except Exception as _e:
            print(f"⚠️ [keep-alive] {_e}")

