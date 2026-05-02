# WOL (Wake-on-LAN) コアライブラリ

from scapy.all import IP, UDP, Raw, send
from config import get_timestamp
import logging

logger = logging.getLogger(__name__)

class WOLService:
    """WOL マジックパケット送信サービス"""

    def __init__(self, broadcast_ip="255.255.255.255", port=9):
        """初期化

        Args:
            broadcast_ip: ブロードキャスト IP アドレス
            port: WOL ポート（デフォルト 9）
        """
        self.broadcast_ip = broadcast_ip
        self.port = port

    @staticmethod
    def validate_mac(mac_address):
        """MAC アドレスの形式検証

        Args:
            mac_address: MAC アドレス文字列 (xx:xx:xx:xx:xx:xx または xx-xx-xx-xx-xx-xx)

        Returns:
            bool: 有効な形式なら True

        Raises:
            ValueError: 無効な形式の場合
        """
        import re
        pattern = r"^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$"
        if not re.match(pattern, mac_address):
            raise ValueError(f"Invalid MAC address format: {mac_address}")
        return True

    @staticmethod
    def create_magic_packet(mac_address):
        """マジックパケットを生成

        Args:
            mac_address: ターゲット MAC アドレス

        Returns:
            bytes: マジックパケット
        """
        # MAC アドレスを正規化（コロン区切りに統一）
        mac = mac_address.replace("-", ":")
        mac_bytes = bytes.fromhex(mac.replace(":", ""))

        # マジックパケット: FF * 6 + MAC * 16
        magic_packet = b"\xff" * 6 + mac_bytes * 16

        return magic_packet

    def send(self, mac_address):
        """WOL パケットを送信

        Args:
            mac_address: ターゲット MAC アドレス

        Returns:
            dict: 実行結果 {"status": "packet_sent", "timestamp": "..."}

        Raises:
            ValueError: 無効な MAC アドレス
            Exception: パケット送信失敗
        """
        try:
            # MAC アドレスの検証
            self.validate_mac(mac_address)

            # マジックパケットの生成
            magic_packet = self.create_magic_packet(mac_address)

            # UDP パケットの構築
            packet = IP(dst=self.broadcast_ip)/UDP(dport=self.port)/Raw(load=magic_packet)

            # パケット送信
            logger.info(f"Sending WOL packet to {mac_address} on {self.broadcast_ip}:{self.port}")
            send(packet, verbose=False)

            return {
                "status": "packet_sent",
                "timestamp": get_timestamp()
            }

        except ValueError as e:
            logger.error(f"Invalid MAC address: {e}")
            raise
        except Exception as e:
            logger.error(f"Failed to send WOL packet: {e}")
            raise
