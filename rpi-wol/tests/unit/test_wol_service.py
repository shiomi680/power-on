"""
WOL サービスの単体テスト
"""

import pytest
import sys
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))

from wol_service import WOLService


class TestWOLService:
    """WOL サービスのテストクラス"""

    @pytest.fixture
    def service(self):
        """WOL サービスのフィクスチャ"""
        return WOLService(broadcast_ip="255.255.255.255", port=9)

    def test_validate_mac_valid_format_colon(self):
        """MAC アドレス検証: コロン区切りの有効形式"""
        mac = "aa:bb:cc:dd:ee:ff"
        assert WOLService.validate_mac(mac) is True

    def test_validate_mac_valid_format_dash(self):
        """MAC アドレス検証: ダッシュ区切りの有効形式"""
        mac = "aa-bb-cc-dd-ee-ff"
        assert WOLService.validate_mac(mac) is True

    def test_validate_mac_valid_format_uppercase(self):
        """MAC アドレス検証: 大文字の有効形式"""
        mac = "AA:BB:CC:DD:EE:FF"
        assert WOLService.validate_mac(mac) is True

    def test_validate_mac_valid_format_mixed(self):
        """MAC アドレス検証: 混合大文字小文字"""
        mac = "Aa:Bb:Cc:Dd:Ee:Ff"
        assert WOLService.validate_mac(mac) is True

    def test_validate_mac_invalid_format_short(self):
        """MAC アドレス検証: 短すぎる形式"""
        mac = "aa:bb:cc"
        with pytest.raises(ValueError):
            WOLService.validate_mac(mac)

    def test_validate_mac_invalid_format_long(self):
        """MAC アドレス検証: 長すぎる形式"""
        mac = "aa:bb:cc:dd:ee:ff:gg"
        with pytest.raises(ValueError):
            WOLService.validate_mac(mac)

    def test_validate_mac_invalid_characters(self):
        """MAC アドレス検証: 無効な文字"""
        mac = "zz:yy:xx:ww:vv:uu"
        with pytest.raises(ValueError):
            WOLService.validate_mac(mac)

    def test_validate_mac_no_separator(self):
        """MAC アドレス検証: セパレータなし"""
        mac = "aabbccddeeff"
        with pytest.raises(ValueError):
            WOLService.validate_mac(mac)

    def test_create_magic_packet_colon_format(self):
        """マジックパケット生成: コロン形式の MAC"""
        mac = "aa:bb:cc:dd:ee:ff"
        packet = WOLService.create_magic_packet(mac)

        # マジックパケットは 6 + 16*6 = 102 バイト
        assert len(packet) == 102

        # 最初の 6 バイトは FF FF FF FF FF FF
        assert packet[:6] == b"\xff\xff\xff\xff\xff\xff"

        # 次の 16 * 6 バイトは MAC アドレスの繰り返し
        mac_bytes = bytes.fromhex("aabbccddeeff")
        for i in range(16):
            assert packet[6 + i*6:6 + (i+1)*6] == mac_bytes

    def test_create_magic_packet_dash_format(self):
        """マジックパケット生成: ダッシュ形式の MAC"""
        mac = "aa-bb-cc-dd-ee-ff"
        packet = WOLService.create_magic_packet(mac)

        # コロン形式と同じ結果
        mac_colon = "aa:bb:cc:dd:ee:ff"
        packet_colon = WOLService.create_magic_packet(mac_colon)
        assert packet == packet_colon

    def test_create_magic_packet_uppercase(self):
        """マジックパケット生成: 大文字の MAC"""
        mac_lower = "aa:bb:cc:dd:ee:ff"
        mac_upper = "AA:BB:CC:DD:EE:FF"

        packet_lower = WOLService.create_magic_packet(mac_lower)
        packet_upper = WOLService.create_magic_packet(mac_upper)

        assert packet_lower == packet_upper

    def test_send_valid_mac(self, service, monkeypatch):
        """WOL パケット送信: 有効な MAC アドレス"""
        # Mock send function
        send_called = []

        def mock_send(packet, verbose=False):
            send_called.append((packet, verbose))

        monkeypatch.setattr("wol_service.send", mock_send)

        # Send WOL packet
        result = service.send("aa:bb:cc:dd:ee:ff")

        # Verify result
        assert result["status"] == "packet_sent"
        assert "timestamp" in result

        # Verify send was called
        assert len(send_called) == 1

    def test_send_invalid_mac(self, service):
        """WOL パケット送信: 無効な MAC アドレス"""
        with pytest.raises(ValueError):
            service.send("invalid:mac:address")

    def test_send_returns_timestamp(self, service, monkeypatch):
        """WOL パケット送信: タイムスタンプが含まれている"""
        def mock_send(packet, verbose=False):
            pass

        monkeypatch.setattr("wol_service.send", mock_send)

        result = service.send("aa:bb:cc:dd:ee:ff")

        # Verify timestamp format (ISO8601)
        assert "timestamp" in result
        assert result["timestamp"].endswith("Z")
        # Should be parseable as ISO format
        from datetime import datetime
        datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))
