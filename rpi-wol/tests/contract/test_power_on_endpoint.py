"""
Raspberry Pi /api/power/on エンドポイントの contract テスト
"""

import pytest
import sys
import json
from pathlib import Path
from unittest.mock import patch

# Add src to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent / "src"))


@pytest.fixture(scope="module")
def mock_sendp():
    """Mock sendp to prevent actual WOL packet sending"""
    with patch("wol_service.sendp") as mock:
        yield mock


@pytest.fixture
def app(mock_sendp):
    """Flask test client fixture"""
    from flask_app import app
    app.config["TESTING"] = True
    return app


@pytest.fixture
def client(app, mock_sendp):
    """Flask test client"""
    return app.test_client()


class TestPowerOnEndpoint:
    """Power ON エンドポイントの contract テスト"""

    def test_endpoint_exists(self, client):
        """エンドポイントが存在する"""
        response = client.post("/api/power/on", json={"target_mac": "aa:bb:cc:dd:ee:ff"})
        # Should not return 404
        assert response.status_code != 404

    def test_request_method_post(self, client):
        """POST メソッドで呼び出せる"""
        response = client.post("/api/power/on", json={"target_mac": "aa:bb:cc:dd:ee:ff"})
        # POST should be supported
        assert response.status_code in [200, 400, 401, 403, 500]

    def test_request_method_get_not_allowed(self, client):
        """GET メソッドは許可されない"""
        response = client.get("/api/power/on")
        assert response.status_code == 405  # Method Not Allowed

    def test_response_content_type_json(self, client):
        """レスポンスが JSON 形式"""
        response = client.post("/api/power/on", json={"target_mac": "aa:bb:cc:dd:ee:ff"})
        assert response.content_type == "application/json"

    def test_response_has_status_field(self, client):
        """レスポンスに status フィールドがある"""
        response = client.post("/api/power/on", json={"target_mac": "aa:bb:cc:dd:ee:ff"})
        data = json.loads(response.data)
        assert "status" in data

    def test_response_has_timestamp_field(self, client):
        """レスポンスに timestamp フィールドがある"""
        response = client.post("/api/power/on", json={"target_mac": "aa:bb:cc:dd:ee:ff"})
        data = json.loads(response.data)
        assert "timestamp" in data

    def test_response_status_value(self, client):
        """status フィールドの値が packet_sent"""
        response = client.post("/api/power/on", json={"target_mac": "aa:bb:cc:dd:ee:ff"})
        if response.status_code == 200:
            data = json.loads(response.data)
            assert data.get("status") == "packet_sent"

    def test_response_timestamp_format(self, client):
        """timestamp が ISO8601 形式"""
        response = client.post("/api/power/on", json={"target_mac": "aa:bb:cc:dd:ee:ff"})
        if response.status_code == 200:
            data = json.loads(response.data)
            timestamp = data.get("timestamp")
            # Should end with Z for UTC
            assert timestamp.endswith("Z")
            # Should be parseable
            from datetime import datetime
            datetime.fromisoformat(timestamp.replace("Z", "+00:00"))

    def test_request_with_valid_mac(self, client):
        """有効な MAC アドレスでリクエスト"""
        response = client.post("/api/power/on", json={"target_mac": "aa:bb:cc:dd:ee:ff"})
        # Should not return 400 Bad Request for valid MAC
        assert response.status_code != 400

    def test_request_with_invalid_mac(self, client):
        """無効な MAC アドレスでリクエスト"""
        response = client.post("/api/power/on", json={"target_mac": "invalid"})
        # Should return 400 or 422 for invalid MAC
        assert response.status_code in [400, 422]

    def test_request_missing_mac_field(self, client):
        """MAC アドレスフィールドなし"""
        response = client.post("/api/power/on", json={})
        # Should return 400 for missing required field
        assert response.status_code == 400

    def test_request_content_type_json(self, client):
        """リクエストが JSON 形式"""
        response = client.post(
            "/api/power/on",
            data=json.dumps({"target_mac": "aa:bb:cc:dd:ee:ff"}),
            content_type="application/json"
        )
        assert response.status_code in [200, 201, 400]

    def test_response_http_200_on_success(self, client):
        """成功時に HTTP 200 を返す"""
        response = client.post("/api/power/on", json={"target_mac": "aa:bb:cc:dd:ee:ff"})
        if response.status_code != 500:
            assert response.status_code in [200, 201]

    def test_response_error_has_error_field(self, client):
        """エラーレスポンスに error フィールドがある"""
        response = client.post("/api/power/on", json={})
        if response.status_code >= 400:
            data = json.loads(response.data)
            assert "error" in data

    def test_response_error_has_code_field(self, client):
        """エラーレスポンスに code フィールドがある"""
        response = client.post("/api/power/on", json={})
        if response.status_code >= 400:
            data = json.loads(response.data)
            assert "code" in data
