# PC 電源管理サービス

PC シャットダウン・状態確認 API サーバー

## 機能

- Flask ベースの REST API サーバー
- グレースフルシャットダウン実行
- PC の状態確認
- Linux (`shutdown` コマンド) 対応

## 使用方法

### インストール（本番環境 - systemd service）

```bash
# 1. ディレクトリ準備
sudo mkdir -p /opt/pc-power
sudo cp -r . /opt/pc-power/
cd /opt/pc-power

# 2. Python パッケージインストール
sudo pip install -e .

# 3. 環境変数設定
sudo cp .env.example .env
sudo nano .env  # 必要に応じて編集

# 4. systemd service インストール
sudo cp pc-power.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable pc-power
sudo systemctl start pc-power

# 5. 状態確認
sudo systemctl status pc-power
sudo journalctl -u pc-power -f  # ログ確認
```

### 開発環境（Flask 直接起動）

```bash
cd pc-power
pip install -r requirements.txt
python src/flask_app.py
```

サーバーはデフォルトで `http://0.0.0.0:5001` で起動。

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
- `FLASK_PORT`: Flask サーバーポート（デフォルト: 5001）
- `LOG_LEVEL`: ログレベル（デフォルト: INFO）
- `SHUTDOWN_TIMEOUT`: シャットダウンタイムアウト（デフォルト: 60 秒）

## トラブルシューティング

### service が起動しない

```bash
# ステータス確認
sudo systemctl status pc-power

# ログ確認
sudo journalctl -u pc-power -n 50

# 手動起動でエラー確認
cd /opt/pc-power
python3 -m pc_power.flask_app
```

### ポート競合エラー

```bash
# 別のプロセスが 5001 を使用していないか確認
sudo lsof -i :5001

# service の設定を変更
sudo nano /etc/systemd/system/pc-power.service
# EnvironmentFile=/opt/pc-power/.env で FLASK_PORT を変更

sudo systemctl daemon-reload
sudo systemctl restart pc-power
```

### シャットダウンコマンドが実行されない

```bash
# shutdown コマンドが利用可能か確認
which shutdown
shutdown --version

# 権限確認（root で実行されているはず）
ps aux | grep pc-power
```
