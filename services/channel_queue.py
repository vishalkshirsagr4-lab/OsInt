


import queue as _queue_mod

_channel_msg_queue = _queue_mod.Queue()
_channel_queue_started = False

def _channel_queue_worker():
    """Background thread that sends queued channel messages with rate limiting."""
    while True:
        try:
            item = _channel_msg_queue.get(timeout=5)
            if item is None:
                break
            fn, args, kwargs = item
            try:
                fn(*args, **kwargs)
            except Exception as e:
                err = str(e)
                if '429' in err:
                    # Extract retry_after from error
                    m = re.search(r'retry after (\d+)', err)
                    wait = int(m.group(1)) + 1 if m else 5
                    print(f"[channel_queue] 429 — waiting {wait}s")
                    time.sleep(wait)
                    try: fn(*args, **kwargs)
                    except Exception as e2: print(f"[channel_queue] retry failed: {e2}")
                else:
                    print(f"[channel_queue] error: {e}")
            finally:
                _channel_msg_queue.task_done()
            time.sleep(0.4)
        except _queue_mod.Empty:
            continue
        except Exception as e:
            print(f"[channel_queue_worker] error: {e}")

def _start_channel_queue():
    """Start the channel message queue worker thread."""
    global _channel_queue_started
    if not _channel_queue_started:
        t = threading.Thread(target=_channel_queue_worker, daemon=True, name="channel_queue")
        t.start()
        _channel_queue_started = True

def _queue_send(fn, *args, **kwargs):
    """Add a send operation to the rate-limited queue."""
    _start_channel_queue()
    _channel_msg_queue.put((fn, args, kwargs))