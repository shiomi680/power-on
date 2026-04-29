# PC 電源管理サービス

PC シャットダウン・状態確認 API サーバー

## 機能

- Flask ベースの REST API サーバー
- グレースフルシャットダウン実行
- PC の状態確認
- Linux (`shutdown` コマンド) 対応

## 使用方法

### インストール

```bash
cd pc-power
pip install -r requirements.txt
```

### Flask サーバー起動

```bash
python src/flask_app.py
```

サーバーはデフォルトで `http://0.0.0.0:5000` で起動。

### CLI コマンド

```bash
# PC をシャットダウン（デフォルト 60 秒）
python -m cli shutdown --timeout 60

# PC の状態確認
python -m cli status

# サーバー起動
python -m cli run-server --port 5000
```

## API エンドポイント

### POST /api/power/shutdown
PC をシャットダウン

リクエスト:
```json
{"timeout": 60}
```

レスポンス:
```json
{"status": "shutdown_initiated", "timestamp": "2026-04-29T12:00:00Z"}
```

### GET /api/power/status
PC の状態確認

レスポンス:
```json
{"status": "online", "timestamp": "2026-04-29T12:00:00Z"}
```

## テスト

```bash
pytest tests/
pytest tests/ --cov=src
```

## 設定

環境変数で設定:
- `FLASK_PORT`: Flask サーバーポート（デフォルト: 5000）
- `LOG_LEVEL`: ログレベル（デフォルト: INFO）
- `SHUTDOWN_TIMEOUT`: シャットダウンタイムアウト（デフォルト: 60 秒）
