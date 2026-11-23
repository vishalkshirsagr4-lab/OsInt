

# Feature → param name mapping (same as user-facing URL)
_API_PARAM_MAP = {
    'mobile_number': 'number',
    'aadhar':        'aadhar',
    'instagram':     'username',
    'ifsc':          'ifsc',
    'vehicle':       'vehicle',
    'gst':           'gst',
    'pan':           'pan',
    'pak_num':       'number',   # pak number also uses 'number'
    'pincode':       'pincode',
    'ff':            'uid',
    'userid':        'userid',
    'username':      'username',
}

def _api_base_url():
    """Get bot's base URL — komalinfobot.onrender.com"""
    url = os.environ.get("RENDER_EXTERNAL_URL", "").strip()
    if not url:
        svc = os.environ.get("RENDER_SERVICE_NAME", "").strip()
        if svc:
            url = f"https://{svc}.onrender.com"
    # ✅ Default fallback = actual Render URL
    return url.rstrip("/") if url else "https://komalinfobot.onrender.com"


def _build_api_url(feature_key: str, api_key: str) -> str:
    """Build API URL in format: BASE/?param={}&key=API_KEY"""
    base = _api_base_url()
    param = _API_PARAM_MAP.get(feature_key, 'query')
    return f"{base}/?{param}={{}}&key={api_key}"


# Normal user APIs
PHONE_API_URL = "/number?key=YOUR_KEY&num=9876543210"
USERID_API_URL = "https://username-usrid-to-num.onrender.com/api/developer/Cyb3rB4nn3r/fast?key=aa0ace3dffa677d50e3ee638e16cb4ea&userid={}"
AADHAR_API_URL = "https://ethicaltabbo.in/api/aadhaar-lookup?key=FREEDEMO&id=AADHAAR_NUMBER"
INSTA_API_URL = "https://ethicaltabbo.in/api/ig-worker?key=FREEDEMO&url=INSTAGRAM_URL"
IFSC_API_URL = "https://ethicaltabbo.in/api/ifsc-lookup?key=FREEDEMO&code=IFSC_CODE"
VEHICLE_API_URL = "https://ethicaltabbo.in/api/vehicle2mobile?key=FREEDEMO&number=VEHICLE_NUMBER"  # Updated
GST_API_URL = "https://gst-to-info.vercel.app/?number={}&key=SH4DAW-D4DY"
EMAIL_API_URL = "https://mafiaosint.com/api/gmail?apikey=Demogmail&email=rohit5@gmail.com"
PAN_API_URL = "https://shadow-osint.vercel.app/?type=pan&query={}&key=SH"
PAK_NUM_API_URL = "https://shadow-osint.vercel.app/?type=pak_num&query={}&key=SH"
PINCODE_API_URL = "https://dg-drift-apis.onrender.com/pincode/843324?key=drift"
UPI_API_URL = "https://ethicaltabbo.in/api/number-to-upi?key=FREEDEMO&number=MOBILE_NUMBER"



USERNAME_TO_NUM_API_URL = "https://username-usrid-to-num.onrender.com/api/developer/Cyb3rB4nn3r/fast?key=aa0ace3dffa677d50e3ee638e16cb4ea&userid={}"

# Premium-only APIs (Hitek)
HITEK_FULL_INFO_API_URL = "https://hitek-info.onrender.com/search?query={}"
HITEK_NUM_INFO_API_URL = "https://sh4dow-d4dy-hi-tek-num-info.vercel.app/?number={}&key=SH4DAW-D4DY"
