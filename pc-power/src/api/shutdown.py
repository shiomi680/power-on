"""
PC /api/power/shutdown エンドポイント実装
"""

from flask import Blueprint, request, jsonify
from ..power_manager import PowerManager
from ..config import get_timestamp, SHUTDOWN_TIMEOUT
import logging

logger = logging.getLogger(__name__)

# ブループリント定義
bp = Blueprint("shutdown", __name__, url_prefix="/api")

# 電源マネージャーインスタンス
power_manager = PowerManager(timeout=SHUTDOWN_TIMEOUT)


@bp.route("/power/shutdown", methods=["POST"])
def shutdown():
    """
    PC シャットダウンエンドポイント

    リクエスト JSON:
    {
        "timeout": 60  (オプション、デフォルト 60 秒)
    }

    レスポンス JSON:
    {
        "status": "shutdown_initiated",
        "timestamp": "ISO8601"
    }
    """
    try:
        data = request.get_json() or {}
        timeout = data.get("timeout", SHUTDOWN_TIMEOUT)

        try:
            result = power_manager.shutdown(timeout)
            logger.info(f"Shutdown initiated with timeout {timeout}s")
            return jsonify(result), 200

        except RuntimeError as e:
            logger.warning(f"Shutdown error: {e}")
            return jsonify({
                "error": str(e),
                "code": "shutdown_failed"
            }), 409

    except Exception as e:
        logger.error(f"Unexpected error in shutdown endpoint: {e}")
        return jsonify({
            "error": "予期しないエラーが発生しました",
            "code": "internal_error"
        }), 500
