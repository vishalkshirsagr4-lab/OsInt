
# ==================== FLASK WEB SERVER (FOR RENDER) ====================
# ✅ CRITICAL: Flask ko PEHLE start karo — port bind hone se pehle Render service kill kar deta hai
# Agar port 10000 pe 60s mein bind nahi hua to Render "Port scan timeout" de ke kill karta hai
# 409 fix ke liye bhi zaruri: agar DB restore + session cleanup zyada time le to Render restart ho jaata hai
from flask import Flask

app = Flask(__name__)