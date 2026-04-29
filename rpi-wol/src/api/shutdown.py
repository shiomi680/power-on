"""
Raspberry Pi /api/power/shutdown エンドポイント実装

PC へのシャットダウンリクエストをプロキシします
"""

from flask import Blueprint, request, jsonify
import sys
from pathlib import Path

# Add src to path for absolute imports
sys.path.insert(0, str(Path(__file__).parent.parent))

from config import get_timestamp, PC_API_TIMEOUT
import logging
import requests

logger = logging.getLogger(__name__)

# ブループリント定義
bp = Blueprint("shutdown", __name__, url_prefix="/api")


@bp.route("/power/shutdown", methods=["POST"])
def shutdown():
    """
    PC シャットダウンプロキシエンドポイント

    リクエスト JSON:
    {
        "pc_address": "xxx.xxx.xxx.xxx",
        "timeout": 60  (オプション)
    }

    レスポンス JSON:
    {
        "status": "shutdown_initiated",
        "timestamp": "ISO8601"
    }
    """
    try:
        data = request.get_json()

        if not data:
            logger.warning("Request body is empty")
            return jsonify({
                "error": "リクエストボディが空です",
                "code": "empty_body"
            }), 400

        pc_address = data.get("pc_address")
        timeout = data.get("timeout", 60)

        if not pc_address:
            logger.warning("pc_address field is missing")
            return jsonify({
                "error": "pc_address フィールドが必須です",
                "code": "missing_field"
            }), 400

        # PC へのシャットダウンリクエスト
        try:
            response = requests.post(
                f"http://{pc_address}:5001/api/power/shutdown",
                json={"timeout": timeout},
                timeout=PC_API_TIMEOUT
            )

            if response.status_code == 200:
                result = response.json()
                logger.info(f"Shutdown initiated on {pc_address}")
                return jsonify(result), 200
            else:
                error_data = response.json() if response.headers.get("content-type") == "application/json" else {}
                logger.error(f"PC returned status {response.status_code}")
                return jsonify({
                    "error": error_data.get("error", "PC がシャットダウンリクエストを処理できません"),
                    "code": error_data.get("code", "pc_error")
                }), 502

        except requests.Timeout:
            logger.warning(f"PC API timeout after {PC_API_TIMEOUT}s")
            return jsonify({
                "error": f"PC の応答がタイムアウトしました（{PC_API_TIMEOUT}秒）",
                "code": "timeout"
            }), 504

        except requests.ConnectionError as e:
            logger.warning(f"Cannot connect to PC: {e}")
            return jsonify({
                "error": f"PC に接続できません: {pc_address}",
                "code": "connection_error"
            }), 503

    except Exception as e:
        logger.error(f"Unexpected error in shutdown endpoint: {e}")
        return jsonify({
            "error": "予期しないエラーが発生しました",
            "code": "internal_error"
        }), 500
