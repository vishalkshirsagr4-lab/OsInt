

def _split_result_by_records(text: str, max_len: int = 3500) -> list:
    """
    Smart message splitter — box UI aware, entity-safe.
    Every output chunk is guaranteed to be wrapped in <blockquote>...</blockquote>.
    Splits by <b>record markers, entity limit (88), char limit (3500).
    """
    import re as _re

    MAX_ENTITIES = 88

    def _fits(chunk: str) -> bool:
        return len(chunk) <= max_len and _count_html_entities(chunk) <= MAX_ENTITIES

    def _wrap(chunk: str) -> str:
        """Ensure chunk is in blockquote. Preserve existing wrapper."""
        c = chunk.strip()
        if c.startswith("<blockquote>") and c.endswith("</blockquote>"):
            return c
        # Extract inner content if partially wrapped
        if c.startswith("<blockquote>"):
            return c + "</blockquote>"
        return f"<blockquote>{c}\n\n{BOT_CREDIT}</blockquote>"

    def _unwrap(chunk: str) -> str:
        """Remove blockquote wrapper to get raw inner content."""
        c = chunk.strip()
        if c.startswith("<blockquote>") and c.endswith("</blockquote>"):
            inner = c[len("<blockquote>"):-len("</blockquote>")]
            # Remove trailing BOT_CREDIT if present
            if inner.rstrip().endswith(BOT_CREDIT):
                inner = inner.rstrip()[:-len(BOT_CREDIT)].rstrip()
            return inner.strip()
        return c

    # Already fits — return as-is
    if _fits(text):
        return [text]

    # Get inner content to work with
    inner_text = _unwrap(text)

    # ── Try splitting by new box-style record markers ──
    # Pattern 1: new UI  👤 ʀᴇᴄᴏʀᴅ N/T
    # Pattern 2: old UI  👤 <b>ʀᴇᴄᴏʀᴅ N</b>
    # Pattern 3: any box  ┌─
    parts_raw = [inner_text]
    for pat in [
        r'(?=\n\n👤 ʀᴇᴄᴏʀᴅ \d+/\d+)',
        r'(?=\n\n?👤 <b>ʀᴇᴄᴏʀᴅ \d+</b>)',
        r'(?=\n\n┌─)',
    ]:
        parts_raw = _re.compile(pat).split(inner_text)
        if len(parts_raw) > 1:
            break

    if len(parts_raw) > 1:
        header_inner = parts_raw[0]   # title + query + total count
        record_parts  = parts_raw[1:] # each is one record block

        chunks_inner = []
        current_inner = header_inner.rstrip()

        for rec in record_parts:
            candidate = current_inner + rec
            test_chunk = _wrap(candidate)
            if _fits(test_chunk):
                current_inner = candidate
            else:
                if current_inner.strip():
                    chunks_inner.append(current_inner.strip())
                current_inner = rec.strip()
                # Single record too long? Line-split it
                test_rec = _wrap(current_inner)
                if not _fits(test_rec):
                    lines = current_inner.split('\n')
                    sub = ""
                    for line in lines:
                        trial = (sub + '\n' + line).strip() if sub else line
                        if _fits(_wrap(trial)):
                            sub = trial
                        else:
                            if sub:
                                chunks_inner.append(sub)
                            sub = line
                    current_inner = sub

        if current_inner.strip():
            chunks_inner.append(current_inner.strip())

        if chunks_inner:
            return [_wrap(c) for c in chunks_inner]

    # ── Last resort: line-by-line split ──
    lines = inner_text.split('\n')
    chunks_inner = []
    current = ""
    for line in lines:
        trial = (current + '\n' + line).strip() if current else line
        if _fits(_wrap(trial)):
            current = trial
        else:
            if current:
                chunks_inner.append(current)
            current = line
    if current:
        chunks_inner.append(current)

    if chunks_inner:
        return [_wrap(c) for c in chunks_inner]

    # Absolute fallback
    return [_wrap(inner_text[:max_len - 100])]