"""
PC /api/power/status エンドポイント実装
"""

from flask import Blueprint, jsonify
from ..power_manager import PowerManager
from ..config import get_timestamp
import logging

logger = logging.getLogger(__name__)

# ブループリント定義
bp = Blueprint("status", __name__, url_prefix="/api")

# 電源マネージャーインスタンス
power_manager = PowerManager()


@bp.route("/power/status", methods=["GET"])
def status():
    """
    PC ステータス確認エンドポイント

    レスポンス JSON:
    {
        "status": "online",
        "timestamp": "ISO8601"
    }
    """
    try:
        result = power_manager.get_status()
        logger.info("Status query")
        return jsonify(result), 200

    except Exception as e:
        logger.error(f"Unexpected error in status endpoint: {e}")
        return jsonify({
            "error": "ステータス取得に失敗しました",
            "code": "status_failed"
        }), 500
