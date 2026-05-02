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


    def test_send_valid_mac(self, service, monkeypatch):
        """WOL パケット送信: 有効な MAC アドレス"""
        # Mock send_magic_packet function
        send_called = []

        def mock_send_magic_packet(mac, ip_address=None, port=None):
            send_called.append((mac, ip_address, port))

        monkeypatch.setattr("wol_service.send_magic_packet", mock_send_magic_packet)

        # Send WOL packet
        result = service.send("aa:bb:cc:dd:ee:ff")

        # Verify result
        assert result["status"] == "packet_sent"
        assert "timestamp" in result

        # Verify send_magic_packet was called
        assert len(send_called) == 1
        assert send_called[0][0] == "aa:bb:cc:dd:ee:ff"

    def test_send_invalid_mac(self, service):
        """WOL パケット送信: 無効な MAC アドレス"""
        with pytest.raises(ValueError):
            service.send("invalid:mac:address")

    def test_send_returns_timestamp(self, service, monkeypatch):
        """WOL パケット送信: タイムスタンプが含まれている"""
        def mock_send_magic_packet(mac, ip_address=None, port=None):
            pass

        monkeypatch.setattr("wol_service.send_magic_packet", mock_send_magic_packet)

        result = service.send("aa:bb:cc:dd:ee:ff")

        # Verify timestamp format (ISO8601)
        assert "timestamp" in result
        assert result["timestamp"].endswith("Z")
        # Should be parseable as ISO format
        from datetime import datetime
        datetime.fromisoformat(result["timestamp"].replace("Z", "+00:00"))
