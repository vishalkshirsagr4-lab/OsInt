from datetime import datetime
import psutil


# HEARTBEAT FUNCTION (ENHANCED)
def get_system_stats():
    try:
        cpu = psutil.cpu_percent(interval=1)
        memory = psutil.virtual_memory()
        mem_used = memory.used / (1024**3)
        mem_total = memory.total / (1024**3)
        disk = psutil.disk_usage('/')
        disk_used = disk.used / (1024**3)
        disk_total = disk.total / (1024**3)
        boot_time = datetime.fromtimestamp(psutil.boot_time())
        uptime = datetime.now() - boot_time
        days = uptime.days
        hours, remainder = divmod(uptime.seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return {
            'cpu': cpu,
            'mem_used': mem_used,
            'mem_total': mem_total,
            'mem_percent': memory.percent,
            'disk_used': disk_used,
            'disk_total': disk_total,
            'disk_percent': disk.percent,
            'uptime': f"{days}d {hours}h {minutes}m"
        }
    except Exception:
        return None