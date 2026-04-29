# PC 電源管理サービス デプロイメントガイド

PC 上に Power On 電源管理サービスをデプロイします。

## 前提条件

- Linux システム（Ubuntu 20.04+ 推奨）
- Docker インストール済み
- Docker Compose V2 以上
- `shutdown` コマンドが実行可能な権限

## クイックスタート

### 1. リポジトリをクローン

```bash
git clone https://github.com/user/power-on.git
cd power-on/pc-power
```

### 2. 環境設定

```bash
# .env ファイルを作成
cp .env.example .env

# 必要に応じて編集（デフォルトで動作します）
nano .env
```

### 設定項目

```bash
# シャットダウンタイムアウト（秒）
SHUTDOWN_TIMEOUT=60

# ロギングレベル
LOG_LEVEL=INFO
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
curl http://localhost:5001/api/health

# ステータス確認
curl http://localhost:5001/api/power/status
```

## 重要: シャットダウン権限の設定

### オプション 1: Docker で sudo を使用（推奨しない）

コンテナが実際にホストをシャットダウンする場合：

```bash
# docker-compose.yml で privileged を有効化
services:
  pc-power:
    privileged: true
    pid: "host"
```

### オプション 2: sudoers を設定（推奨）

```bash
# sudoers に追加（root で実行）
sudo visudo

# 以下の行を追加
docker ALL=(ALL) NOPASSWD: /sbin/shutdown
```

### オプション 3: テスト用（シャットダウンなし）

デバッグ・テスト時はシャットダウンを実行せず、ログのみ出力:

```bash
# docker-compose.yml で以下を設定
environment:
  - SHUTDOWN_COMMAND=echo "Shutdown scheduled"
```

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

### コンテナが起動しない

```bash
# コンテナが起動しているか確認
docker compose ps

# ログでエラーを確認
docker compose logs
```

### Raspberry Pi から接続できない

```bash
# ネットワークをテスト
docker compose exec pc-power curl http://localhost:5001/api/health

# PC のファイアウォール設定を確認
sudo ufw status
```

### シャットダウンが実行されない

```bash
# コンテナのシャットダウンコマンドをテスト
docker compose exec pc-power shutdown -h +1

# キャンセル
docker compose exec pc-power shutdown -c
```

## システムブートで自動起動

PC を起動時に自動的にコンテナを起動するには:

```bash
# systemd サービスファイルを作成
sudo nano /etc/systemd/system/power-on-pc.service
```

以下の内容を記入:

```ini
[Unit]
Description=Power On - PC Power Management Service
After=docker.service
Requires=docker.service

[Service]
Type=oneshot
User=your-username
WorkingDirectory=/home/your-username/power-on/pc-power
ExecStart=/usr/bin/docker compose up -d
ExecStop=/usr/bin/docker compose down
RemainAfterExit=yes

[Install]
WantedBy=multi-user.target
```

有効化:

```bash
sudo systemctl daemon-reload
sudo systemctl enable power-on-pc.service
sudo systemctl start power-on-pc.service
```

## ネットワーク設定

### ローカルネットワークのみ（推奨）

デフォルト設定:

```yaml
ports:
  - "5001:5001"  # localhost のみアクセス可能
```

### 特定の IP からアクセス可能に

```yaml
ports:
  - "192.168.1.100:5001:5001"
```

### 外部ネットワークからのアクセス（セキュリティ注意）

```yaml
ports:
  - "0.0.0.0:5001:5001"
```

ファイアウォール設定:

```bash
# ポート 5001 を許可
sudo ufw allow 5001
```

## リバースプロキシ経由でのアクセス（上級）

nginx でリバースプロキシを設定:

```nginx
server {
    listen 80;
    server_name your-pc-domain.com;

    location /api/power {
        proxy_pass http://localhost:5001;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }
}
```

## パフォーマンス最適化

### メモリ制限

```yaml
services:
  pc-power:
    deploy:
      resources:
        limits:
          memory: 256M
```

### ログローテーション

```yaml
services:
  pc-power:
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
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

## CLI コマンドテスト

```bash
# ステータス確認
docker compose exec pc-power python -m cli status

# シャットダウンテスト（1分後）
docker compose exec pc-power python -m cli shutdown --timeout 60

# JSON 出力
docker compose exec pc-power python -m cli status --json
```

## セキュリティに関する注意

- **シャットダウン権限**: `privileged: true` を使用する場合、コンテナ内の任意のコマンドが root 権限で実行可能になります
- **ネットワークアクセス**: 外部からのアクセスを許可する場合、認証やファイアウォール設定を必ず実施してください
- **ログ記録**: シャットダウン関連のログを監視してください

## サポート

問題が発生した場合:

1. `docker compose logs` でログを確認
2. `docker compose ps` でコンテナ状態を確認
3. ファイアウォール設定を確認
4. Raspberry Pi からの接続をテスト
