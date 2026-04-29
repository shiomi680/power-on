# Raspberry Pi WOL サービス デプロイメントガイド

Raspberry Pi 上に Power On Web UI + WOL サービスをデプロイします。

## 前提条件

- Raspberry Pi 3B+ 以上
- Docker インストール済み
- Docker Compose V2 以上
- 同一ネットワーク内に PC が存在

## クイックスタート

### 1. リポジトリをクローン

```bash
git clone https://github.com/user/power-on.git
cd power-on/rpi-wol
```

### 2. 環境設定

```bash
# .env ファイルを作成
cp .env.example .env

# エディタで編集
nano .env
```

### 重要な設定項目

```bash
# PC のアドレス（IP または hostname）
PC_ADDRESS=192.168.1.100

# ターゲット PC の MAC アドレス
WOL_TARGET_MAC=aa:bb:cc:dd:ee:ff

# ブロードキャスト IP（通常は変更不要）
WOL_BROADCAST_IP=255.255.255.255
```

### 3. イメージをビルド

```bash
docker compose build
```

### 4. コンテナを起動

```bash
docker compose up -d
```

### 5. 動作確認

```bash
# ヘルスチェック
curl http://localhost:5000/api/health

# Web UI にアクセス
curl http://localhost:5000
```

ブラウザで `http://raspberry-pi-ip:5000` にアクセスして Web UI が表示されることを確認してください。

## ログの確認

```bash
# リアルタイムログ
docker compose logs -f

# 過去のログ
docker compose logs

# 最後の 50 行
docker compose logs --tail 50
```

## 停止・再起動

```bash
# 停止
docker compose down

# 再起動
docker compose restart

# 再構築して起動
docker compose up -d --build
```

## トラブルシューティング

### Web UI が表示されない

```bash
# コンテナが起動しているか確認
docker compose ps

# ログでエラーを確認
docker compose logs
```

### PC が起動しない（WOL）

1. MAC アドレスが正しいか確認
2. PC の BIOS で WOL を有効化
3. ネットワーク接続を確認

```bash
# WOL パケット送信テスト
docker compose exec rpi-wol python -m cli send-wol --mac aa:bb:cc:dd:ee:ff
```

### PC に接続できない

```bash
# ネットワークをテスト
docker compose exec rpi-wol ping pc-power-ip
```

## システムブートで自動起動

Raspberry Pi を再起動時に自動的にコンテナを起動するには:

```bash
# systemd サービスファイルを作成
sudo nano /etc/systemd/system/power-on-rpi.service
```

以下の内容を記入:

```ini
[Unit]
Description=Power On - Raspberry Pi WOL Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=pi
WorkingDirectory=/home/pi/power-on/rpi-wol
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

有効化:

```bash
sudo systemctl daemon-reload
sudo systemctl enable power-on-rpi.service
sudo systemctl start power-on-rpi.service
```

## パフォーマンス最適化

### Raspberry Pi のメモリが限定的な場合

```bash
# メモリ使用量を制限
# docker-compose.yml に以下を追加
services:
  rpi-wol:
    deploy:
      resources:
        limits:
          memory: 256M
```

### ディスク容量を節約

```bash
# ログローテーション設定
# docker-compose.yml に以下を追加
services:
  rpi-wol:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
```

## ネットワーク設定

### 外部ネットワークからのアクセス

デフォルトではローカルネットワークのみアクセス可能です。

セキュリティが必要な場合は、ファイアウォールで制限してください:

```bash
# Raspberry Pi のポート 5000 を許可
sudo ufw allow 5000
```

### リバースプロキシ経由でのアクセス（上級）

nginx でリバースプロキシを設定:

```nginx
server {
    listen 80;
    server_name your-domain.com;

    location / {
        proxy_pass http://localhost:5000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## バージョンアップ

```bash
# 新しいコードをプル
git pull origin main

# イメージを再構築
docker compose build --no-cache

# 再起動
docker compose up -d
```

## サポート

問題が発生した場合:

1. `docker compose logs` でログを確認
2. `docker compose ps` でコンテナ状態を確認
3. PC への接続をテスト (`ping`, `curl`)
4. MAC アドレス設定を確認
