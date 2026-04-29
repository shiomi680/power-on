# Raspberry Pi WOL サービス

Web UI ホスティング + Wake-on-LAN (WOL) パケット送信サービス

## 機能

- Web UI（HTML/CSS/JavaScript）で PC の電源制御
- WOL マジックパケット送信で PC をリモート起動
- Flask バックエンド API サーバー
- 状態確認 API

## 使用方法

### インストール

```bash
cd rpi-wol
pip install -r requirements.txt
```

### Flask サーバー起動

```bash
python src/flask_app.py
```

サーバーはデフォルトで `http://0.0.0.0:5000` で起動。ブラウザから `http://rpi-address:5000` にアクセス。

### CLI コマンド

```bash
# WOL パケット送信
python -m cli send-wol --mac xx:xx:xx:xx:xx:xx

# サーバー起動
python -m cli run-server --port 5000
```

## API エンドポイント

### POST /api/power/on
WOL パケット送信

リクエスト:
```json
{"target_mac": "xx:xx:xx:xx:xx:xx"}
```

レスポンス:
```json
{"status": "packet_sent", "timestamp": "2026-04-29T12:00:00Z"}
```

### GET /
Web UI ホームページ

## テスト

```bash
pytest tests/
pytest tests/ --cov=src
```

## 設定

環境変数で設定:
- `FLASK_PORT`: Flask サーバーポート（デフォルト: 5000）
- `LOG_LEVEL`: ログレベル（デフォルト: INFO）
