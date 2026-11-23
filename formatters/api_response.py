
def _clean_api_result(result: dict) -> dict:
    """Remove internal keys from API response."""
    _SKIP = {'pic_file', 'source', '_raw', 'developer', 'dev', 'Developer'}
    return {k: v for k, v in result.items() if k not in _SKIP}