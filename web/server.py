
def run_web():
    app.run(host='0.0.0.0', port=10000, use_reloader=False, threaded=True)


_web_thread = threading.Thread(target=run_web, daemon=True, name="flask")
_web_thread.start()
time.sleep(0.5)  # Flask ko bind hone do
print("✅ Flask web server started on port 10000")