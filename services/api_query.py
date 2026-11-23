


def _run_feature_query(feature_key: str, query: str):
    """Route query to correct feature function. Returns result dict or None."""
    import re as _re
    
    if feature_key == 'mobile_number':
        clean = _re.sub(r'[^\d+]', '', query)
        if not _re.match(r'^\+?\d{7,15}$', clean):
            return None, 'Invalid mobile number. Example: 9876543210'
        return get_number_info(clean), None

    elif feature_key == 'aadhar':
        clean = _re.sub(r'[\s-]', '', query)
        if not _re.match(r'^\d{12}$', clean):
            return None, 'Invalid Aadhar. Must be 12 digits'
        return get_aadhar_info(clean), None

    elif feature_key == 'instagram':
        clean = query.lstrip('@').strip()
        if not clean:
            return None, 'Invalid Instagram username'
        r = get_instagram_info(clean)
        if isinstance(r, dict): r.pop('pic_file', None)
        return r, None

    elif feature_key == 'username':
        clean = query.lstrip('@').strip()
        if not clean:
            return None, 'Invalid username'
        try:
            r = get_instagram_info(clean)
            if isinstance(r, dict): r.pop('pic_file', None)
            return r, None
        except Exception as e:
            return None, f'Username lookup error: {e}' 

    elif feature_key == 'ifsc':
        clean = query.upper().strip()
        if len(clean) != 11:
            return None, 'IFSC must be 11 characters. Example: SBIN0001234'
        return get_ifsc_info(clean), None

    elif feature_key == 'vehicle':
        clean = _re.sub(r'\s+', '', query).upper()
        if len(clean) < 6:
            return None, 'Invalid RC number. Example: MH12AB1234'
        r = get_vehicle_info(clean)
        if isinstance(r, dict): r.pop('_raw', None)
        return r, None

    elif feature_key == 'gst':
        clean = query.upper().strip()
        if len(clean) < 10:
            return None, 'Invalid GST. Example: 10DJCPK4351Q1Z5'
        r = get_gst_info(clean)
        if isinstance(r, dict): r.pop('_raw', None)
        return r, None

    elif feature_key == 'pan':
        clean = query.upper().strip()
        if not _re.match(r'^[A-Z]{5}[0-9]{4}[A-Z]$', clean):
            return None, 'Invalid PAN. Example: AAMTS3432L'
        r = get_pan_info(clean)
        if isinstance(r, dict): r.pop('_raw', None)
        return r, None

    elif feature_key == 'pak_num':
        clean = _re.sub(r'[^\d]', '', query)
        if len(clean) < 7:
            return None, 'Invalid Pakistan number'
        r = get_pak_num_info(clean)
        if isinstance(r, dict): r.pop('_raw', None)
        return r, None

    elif feature_key == 'pincode':
        clean = _re.sub(r'[^\d]', '', query)
        if len(clean) != 6:
            return None, 'Pincode must be 6 digits. Example: 110001'
        r = get_pincode_info(clean)
        if isinstance(r, dict): r.pop('_raw', None)
        return r, None

    elif feature_key in ('ff', 'ff_info'):
        clean = _re.sub(r'[^\d]', '', query)
        if not clean:
            return None, 'Free Fire UID must be numeric'
        return get_ff_info(clean), None

    elif feature_key == 'userid':
        clean = _re.sub(r'[^\d]', '', query)
        if not clean:
            return None, 'User ID must be numeric'
        return {'success': True, 'user_id': clean, 'note': 'Use bot for full TG user info'}, None

    return None, f'Feature "{feature_key}" not supported'


