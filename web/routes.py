

@app.route('/', methods=['GET', 'POST'])
def home():
    """
    Bot root URL — doubles as API endpoint.
    
    Normal visit:  https://boturl/           → "Bot is running ✅"
    API call:      https://komalinfobot.onrender.com/?number=9876543210&key=KOMAL-XXXX  → JSON data
    """
    from flask import request as _req, jsonify as _json
    import re as _re

    # Check if this is an API call (has 'key' param)
    api_key = (_req.args.get('key') or _req.args.get('api_key') or '').strip()
    
    # No key = normal visit, show bot status
    if not api_key:
        return "Bot is running ✅", 200

    # Has key = API call, validate and process
    vr = validate_api_key(api_key)
    if not vr['valid']:
        return _json({'success': False, 'error': vr['error']}), 401

    feature_key = vr['feature_key']
    expected_param = _API_PARAM_MAP.get(feature_key, 'query')

    # Get query value — try expected param first, then any non-key param
    query_value = _req.args.get(expected_param, '').strip()
    if not query_value:
        for k, v in _req.args.items():
            if k not in ('key', 'api_key'):
                query_value = v.strip()
                break

    if not query_value:
        return _json({
            'success': False,
            'error': f'Query value missing',
            'usage': f'/?{expected_param}=VALUE&key=YOUR_KEY',
            'feature': feature_key
        }), 400

    # Run feature query using bot internal APIs
    try:
        result, err = _run_feature_query(feature_key, query_value)
    except Exception as e:
        return _json({'success': False, 'error': f'Server error: {e}'}), 500

    if err:
        return _json({'success': False, 'error': err}), 400

    if not result or (isinstance(result, dict) and not result.get('success', True)):
        return _json({'success': False, 'error': (result or {}).get('msg', 'No data found'), 'query': query_value}), 404

    if isinstance(result, dict):
        result = _clean_api_result(result)

    # ✅ Deduct credit per API call — SABKE liye (premium, owner, normal sab)
    api_cost = get_api_credit_cost(feature_key, 1)  # per-call cost
    user_id = vr['user_id']
    credits_left = get_credits(user_id)

    # Credits check — convert "∞" to actual number for API (owner bhi pay karega)
    try:
        credits_int = int(credits_left) if str(credits_left) != '∞' else 999999
    except Exception:
        credits_int = 0

    if credits_int < api_cost:
        return _json({
            'success': False,
            'error': f'Insufficient credits. Need {api_cost}, have {credits_left}. Recharge via bot.',
            'credits_left': credits_left
        }), 402

    # Deduct from DB — sab users ke liye including premium
    if str(credits_left) == '∞':
        # Owner ke liye DB se nahi katenge but response mein 0 dikhayenge
        credits_after = '∞'
    else:
        remove_credits(user_id, api_cost)
        credits_after = get_credits(user_id)

    return _json({
        'success': True,
        'feature': feature_key,
        'query': query_value,
        'data': result,
        'key_expires': vr['expires_at'],
        'credits_used': api_cost,
        'credits_left': credits_after
    })



@app.route('/api/features', methods=['GET'])
def api_features_list():
    """List all available API features with exact URL format."""
    from flask import jsonify as _json
    base = _api_base_url()
    return _json({
        'bot_url': base,
        'url_format': f'{base}/?PARAM=VALUE&key=YOUR_API_KEY',
        'note': 'Same base URL, only param name and key changes per feature',
        'features': {
            'mobile_number': {'param': 'number',   'url': f'{base}/?number={{}}&key=YOUR_KEY',   'example': f'{base}/?number=9876543210&key=YOUR_KEY'},
            'aadhar':        {'param': 'aadhar',   'url': f'{base}/?aadhar={{}}&key=YOUR_KEY',   'example': f'{base}/?aadhar=123456789012&key=YOUR_KEY'},
            'instagram':     {'param': 'username', 'url': f'{base}/?username={{}}&key=YOUR_KEY', 'example': f'{base}/?username=someuser&key=YOUR_KEY'},
            'ifsc':          {'param': 'ifsc',     'url': f'{base}/?ifsc={{}}&key=YOUR_KEY',     'example': f'{base}/?ifsc=SBIN0001234&key=YOUR_KEY'},
            'vehicle':       {'param': 'vehicle',  'url': f'{base}/?vehicle={{}}&key=YOUR_KEY',  'example': f'{base}/?vehicle=MH12AB1234&key=YOUR_KEY'},
            'gst':           {'param': 'gst',      'url': f'{base}/?gst={{}}&key=YOUR_KEY',      'example': f'{base}/?gst=10DJCPK4351Q1Z5&key=YOUR_KEY'},
            'pan':           {'param': 'pan',      'url': f'{base}/?pan={{}}&key=YOUR_KEY',      'example': f'{base}/?pan=AAMTS3432L&key=YOUR_KEY'},
            'pak_num':       {'param': 'number',   'url': f'{base}/?number={{}}&key=YOUR_KEY',   'example': f'{base}/?number=03001234567&key=YOUR_KEY'},
            'pincode':       {'param': 'pincode',  'url': f'{base}/?pincode={{}}&key=YOUR_KEY',  'example': f'{base}/?pincode=110001&key=YOUR_KEY'},
            'ff':            {'param': 'uid',      'url': f'{base}/?uid={{}}&key=YOUR_KEY',      'example': f'{base}/?uid=123456789&key=YOUR_KEY'},
        },
        'generate_key': 'Bot → 🔑 My API Keys → ➕ Generate API'
    })
