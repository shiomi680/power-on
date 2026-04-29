# Docker デプロイメントガイド

Docker を使用して Power On システムをデプロイします。

## 前提条件

- Docker 20.10+
- Docker Compose 1.29+
- Linux kernel 対応の WOL 機能（Raspberry Pi）

## 環境構成

```
┌──────────────────┐
│   User Browser   │
│  (any device)    │
└────────┬─────────┘
         │ HTTP
         │ :5000
┌────────▼─────────────────────┐
│  Docker Container: rpi-wol   │
│  - Flask Web UI              │
│  - WOL パケット送信          │
│  - PC プロキシAPI            │
└────────┬─────────────────────┘
         │ HTTP :5001
┌────────▼─────────────────────┐
│ Docker Container: pc-power   │
│ - PC シャットダウン API      │
│ - PC ステータス確認          │
└──────────────────────────────┘
```

## クイックスタート

### 1. イメージのビルド

```bash
docker compose build
```

または個別にビルド:

```bash
# Raspberry Pi イメージ
docker build -t power-on-rpi:latest ./rpi-wol

# PC イメージ
docker build -t power-on-pc:latest ./pc-power
```

### 2. コンテナの起動

```bash
docker compose up -d
```

### 3. アクセス確認

```bash
# Web UI (Raspberry Pi)
curl http://localhost:5000

# ヘルスチェック
curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
```

### 4. ブラウザでアクセス

```
http://localhost:5000
```

## 環境変数設定

`.env` ファイルで環境変数を指定:

```bash
# .env ファイルを作成
cat > .env << EOF
WOL_TARGET_MAC=aa:bb:cc:dd:ee:ff
WOL_BROADCAST_IP=255.255.255.255
LOG_LEVEL=INFO
EOF

# 起動
docker compose up -d
```

### Raspberry Pi コンテナの環境変数

| 変数名 | デフォルト | 説明 |
|--------|-----------|------|
| `FLASK_HOST` | 0.0.0.0 | Flask バインドホスト |
| `FLASK_PORT` | 5000 | Flask ポート |
| `PC_ADDRESS` | pc-power | PC の IP/hostname |
| `PC_API_PORT` | 5001 | PC API ポート |
| `PC_API_TIMEOUT` | 5 | PC API タイムアウト（秒） |
| `WOL_TARGET_MAC` | aa:bb:cc:dd:ee:ff | ターゲット PC の MAC |
| `WOL_BROADCAST_IP` | 255.255.255.255 | WOL ブロードキャスト IP |
| `LOG_LEVEL` | INFO | ログレベル |

### PC コンテナの環境変数

| 変数名 | デフォルト | 説明 |
|--------|-----------|------|
| `FLASK_HOST` | 0.0.0.0 | Flask バインドホスト |
| `FLASK_PORT` | 5001 | Flask ポート |
| `SHUTDOWN_TIMEOUT` | 60 | シャットダウンタイムアウト（秒） |
| `LOG_LEVEL` | INFO | ログレベル |

## 運用管理

### ログ確認

```bash
# すべてのログ
docker compose logs -f

# 特定サービスのログ
docker compose logs -f rpi-wol
docker compose logs -f pc-power
```

### コンテナの停止

```bash
docker compose down
```

### コンテナの再起動

```bash
docker compose restart
```

### コンテナの再構築

```bash
docker compose up -d --build
```

## ネットワーク設定

### Docker Compose での通信

docker compose 内のコンテナ間通信は自動的に設定されます:

- `rpi-wol` → `pc-power` は hostname `pc-power` でアクセス可能
- PC_ADDRESS を `pc-power` に設定（デフォルト）

### 外部ネットワークからのアクセス

Raspberry Pi コンテナのポート 5000 を外部に公開:

```yaml
# docker compose.yml の rpi-wol セクション
ports:
  - "0.0.0.0:5000:5000"  # すべてのインターフェースで受信
  # または
  - "192.168.1.10:5000:5000"  # 特定のインターフェースのみ
```

## トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker compose logs rpi-wol
docker compose logs pc-power

# ポートが既に使用されていないか確認
lsof -i :5000
lsof -i :5001
```

### Web UI が表示されない

1. ブラウザのキャッシュをクリア
2. `http://localhost:5000/` (末尾のスラッシュを確認)
3. ファイアウォール設定を確認

### PC が起動しない（WOL）

1. MAC アドレスが正しいか確認
2. PC の BIOS で WOL を有効化
3. ネットワーク接続を確認

```bash
# WOL テスト
docker exec power-on-rpi python -m cli send-wol --mac aa:bb:cc:dd:ee:ff
```

## プロダクション デプロイメント

### セキュリティ設定

```yaml
# docker compose.yml
services:
  rpi-wol:
    ports:
      - "5000:5000"  # localhost のみ
    networks:
      - power-on-network
    restart: always
```

### リソース制限

```yaml
services:
  rpi-wol:
    deploy:
      resources:
        limits:
          cpus: '0.5'
          memory: 256M
        reservations:
          cpus: '0.25'
          memory: 128M
```

### ログの永続化

```yaml
services:
  rpi-wol:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## Raspberry Pi 実機へのデプロイ

### オプション 1: docker compose で実行

```bash
# Raspberry Pi にログイン
ssh pi@raspberry-pi

# リポジトリをクローン
git clone https://github.com/user/power-on.git
cd power-on

# 起動
docker compose up -d
```

### オプション 2: Pre-built イメージを使用

```bash
docker pull ghcr.io/user/power-on-rpi:latest
docker pull ghcr.io/user/power-on-pc:latest

docker run -d \
  --name power-on-rpi \
  -p 5000:5000 \
  -e WOL_TARGET_MAC=aa:bb:cc:dd:ee:ff \
  ghcr.io/user/power-on-rpi:latest
```

## イメージサイズ最適化

両イメージとも slim ベースイメージを使用して最小化:

```bash
# イメージサイズ確認
docker images | grep power-on
```

**想定サイズ**:
- `power-on-rpi`: ~200MB
- `power-on-pc`: ~180MB

## 参考資料

- [Docker 公式ドキュメント](https://docs.docker.com/)
- [Docker Compose リファレンス](https://docs.docker.com/compose/compose-file/)
- [Flask Docker ベストプラクティス](https://flask.palletsprojects.com/en/2.3.x/deploying/docker/)
