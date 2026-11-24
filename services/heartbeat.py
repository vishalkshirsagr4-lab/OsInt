

def heartbeat():
    while True:
        try:
            if not LOGS_CHANNEL:  # ✅ FIX: skip if not configured
                time.sleep(300); continue
            stats = get_system_stats()
            if stats:
                IST = ZoneInfo("Asia/Kolkata")
                now_ist = datetime.now(IST)
                render_svc = os.environ.get('RENDER_SERVICE_NAME', 'N/A')
                render_region = os.environ.get('RENDER_REGION', 'N/A')
                render_instance = os.environ.get('RENDER_INSTANCE_ID', 'N/A')[:12] if os.environ.get('RENDER_INSTANCE_ID') else 'N/A'
                render_git = os.environ.get('RENDER_GIT_COMMIT', 'N/A')[:8] if os.environ.get('RENDER_GIT_COMMIT') else 'N/A'
                db_size = os.path.getsize('bot.db') // 1024 if os.path.exists('bot.db') else 0
                heartbeat_text = (
                    f"❤️ <b>ʜᴇᴀʀᴛʙᴇᴀᴛ</b>\n"
                    f"🕐 <b>Time (IST):</b> {now_ist.strftime('%d %b %Y %I:%M:%S %p')}\n"
                    f"━━━━━━━━━━━━━\n"
                    f"🖥️ <b>Host:</b> Render Free\n"
                    f"📛 <b>Service:</b> {render_svc}\n"
                    f"🌍 <b>Region:</b> {render_region}\n"
                    f"🔢 <b>Instance:</b> {render_instance}\n"
                    f"📝 <b>Commit:</b> {render_git}\n"
                    f"━━━━━━━━━━━━━\n"
                    f"⚙️ <b>CPU:</b> {stats['cpu']}%\n"
                    f"💾 <b>RAM:</b> {stats['mem_used']:.1f}GB / {stats['mem_total']:.1f}GB ({stats['mem_percent']}%)\n"
                    f"💽 <b>Disk:</b> {stats['disk_used']:.1f}GB / {stats['disk_total']:.1f}GB ({stats['disk_percent']}%)\n"
                    f"⏱️ <b>Uptime:</b> {stats['uptime']}\n"
                    f"🗄️ <b>DB Size:</b> {db_size} KB"
                )
            else:
                heartbeat_text = f"❤️ <b>ʜᴇᴀʀᴛʙᴇᴀᴛ</b>\n━━━━━━━━━━━━━━━━━━\n✅ <b>Bot is alive</b>\n📅 <b>Time:</b> {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
            formatted = f"<blockquote>{heartbeat_text}\n━━━━━━━━━━━━━━━━━━\n{BOT_CREDIT}</blockquote>"
            # ✅ FIX: Always use _real_bot — heartbeat runs outside any clone context
            _real_bot.send_message(LOGS_CHANNEL, formatted, parse_mode='HTML')
        except Exception: pass
        time.sleep(300)  # 5 minutes