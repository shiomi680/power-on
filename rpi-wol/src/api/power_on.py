"""
Raspberry Pi /api/power/on エンドポイント実装
"""

from flask import Blueprint, request, jsonify
from ..wol_service import WOLService
from ..config import get_timestamp, WOL_BROADCAST_IP, WOL_PORT
import logging

logger = logging.getLogger(__name__)

# ブループリント定義
bp = Blueprint("power_on", __name__, url_prefix="/api")

# WOL サービスインスタンス
wol_service = WOLService(broadcast_ip=WOL_BROADCAST_IP, port=WOL_PORT)


@bp.route("/power/on", methods=["POST"])
def power_on():
    """
    WOL パケット送信エンドポイント

    リクエスト JSON:
    {
        "target_mac": "xx:xx:xx:xx:xx:xx"
    }

    レスポンス JSON:
    {
        "status": "packet_sent",
        "timestamp": "ISO8601"
    }
    """
    try:
        # リクエストデータの取得
        data = request.get_json()

        if not data:
            logger.warning("Request body is empty")
            return jsonify({
                "error": "リクエストボディが空です",
                "code": "empty_body"
            }), 400

        # MAC アドレスの取得と検証
        target_mac = data.get("target_mac")

        if not target_mac:
            logger.warning("target_mac field is missing")
            return jsonify({
                "error": "target_mac フィールドが必須です",
                "code": "missing_field"
            }), 400

        # WOL パケット送信
        try:
            WOLService.validate_mac(target_mac)
            result = wol_service.send(target_mac)
            logger.info(f"WOL packet sent successfully to {target_mac}")
            return jsonify(result), 200

        except ValueError as e:
            logger.error(f"Invalid MAC address: {e}")
            return jsonify({
                "error": f"無効な MAC アドレス形式: {str(e)}",
                "code": "invalid_mac"
            }), 400

        except Exception as e:
            logger.error(f"Failed to send WOL packet: {e}")
            return jsonify({
                "error": "WOL パケット送信に失敗しました",
                "code": "send_failed"
            }), 500

    except Exception as e:
        logger.error(f"Unexpected error in power_on endpoint: {e}")
        return jsonify({
            "error": "予期しないエラーが発生しました",
            "code": "internal_error"
        }), 500
