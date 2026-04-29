"""
Raspberry Pi /api/status エンドポイント実装

PC の状態を確認するためのプロキシエンドポイント
"""

from flask import Blueprint, jsonify
import sys
from pathlib import Path

# Add src to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_timestamp, PC_ADDRESS, PC_API_TIMEOUT
import logging
import requests

logger = logging.getLogger(__name__)

# ブループリント定義
bp = Blueprint("status", __name__, url_prefix="/api")


@bp.route("/status", methods=["GET"])
def status():
    """
    PC の状態確認エンドポイント

    レスポンス JSON:
    {
        "status": "online|offline|unknown",
        "timestamp": "ISO8601"
    }
    """
    try:
        if not PC_ADDRESS:
            logger.warning("PC_ADDRESS not configured")
            return jsonify({
                "status": "unknown",
                "timestamp": get_timestamp()
            }), 200

        # PC の API を呼び出し
        try:
            response = requests.get(
                f"http://{PC_ADDRESS}:5001/api/power/status",
                timeout=PC_API_TIMEOUT
            )

            if response.status_code == 200:
                logger.info(f"PC status: online")
                return jsonify({
                    "status": "online",
                    "timestamp": get_timestamp()
                }), 200
            else:
                logger.warning(f"PC API returned status {response.status_code}")
                return jsonify({
                    "status": "unknown",
                    "timestamp": get_timestamp()
                }), 200

        except requests.Timeout:
            logger.warning(f"PC API timeout after {PC_API_TIMEOUT}s")
            return jsonify({
                "status": "offline",
                "timestamp": get_timestamp()
            }), 200

        except requests.ConnectionError as e:
            logger.warning(f"Cannot connect to PC: {e}")
            return jsonify({
                "status": "offline",
                "timestamp": get_timestamp()
            }), 200

    except Exception as e:
        logger.error(f"Unexpected error in status endpoint: {e}")
        return jsonify({
            "status": "unknown",
            "timestamp": get_timestamp()
        }), 200
