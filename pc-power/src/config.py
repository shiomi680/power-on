import os
from datetime import datetime

# Flask 設定
FLASK_PORT = int(os.getenv("FLASK_PORT", 5001))
FLASK_HOST = os.getenv("FLASK_HOST", "0.0.0.0")
FLASK_DEBUG = os.getenv("FLASK_DEBUG", "False").lower() == "true"

# 電源管理設定
SHUTDOWN_TIMEOUT = int(os.getenv("SHUTDOWN_TIMEOUT", 60))
SHUTDOWN_COMMAND = os.getenv("SHUTDOWN_COMMAND", "shutdown -h +1")

# ロギング設定
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")

def get_timestamp():
    """ISO8601 タイムスタンプを取得"""
    return datetime.utcnow().isoformat() + "Z"
