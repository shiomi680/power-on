import os
from datetime import datetime

# Flask 設定
FLASK_PORT = int(os.getenv("FLASK_PORT", 5000))
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# WOL 設定
WOL_TARGET_MAC = os.getenv("WOL_TARGET_MAC", "")
WOL_BROADCAST_IP = os.getenv("WOL_BROADCAST_IP", "255.255.255.255")
WOL_PORT = int(os.getenv("WOL_PORT", 9))

# PC リモート設定
PC_ADDRESS = os.getenv("PC_ADDRESS", "")
PC_API_PORT = int(os.getenv("PC_API_PORT", 5001))
PC_API_TIMEOUT = int(os.getenv("PC_API_TIMEOUT", 5))

# ロギング設定
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def get_timestamp():
    """ISO8601 タイムスタンプを取得"""
    return datetime.utcnow().isoformat() + "Z"
