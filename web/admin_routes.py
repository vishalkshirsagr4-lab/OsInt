

@app.route('/backup-now')
def backup_now_endpoint():
    """Manual backup — synchronous."""
    try:
        _wal_checkpoint()
        ok = github_upload_db()
        db_size = os.path.getsize('bot.db') // 1024 if os.path.exists('bot.db') else 0
        return (f"Backup SUCCESS! {db_size}KB → GitHub" if ok else "Backup FAILED — check logs!"), (200 if ok else 500)
    except Exception as e:
        return f"Error: {e}", 500