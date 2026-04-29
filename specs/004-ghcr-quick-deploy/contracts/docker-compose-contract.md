# コントラクト: docker-compose.yml ファイル形式

**日付**: 2026-04-29  
**対象**: root docker-compose.yml、rpi-wol/docker-compose.yml、pc-power/docker-compose.yml

## コントラクト定義

### 必須フィールド

```yaml
# Required fields for all docker-compose.yml files
version: '3.8'                    # Compose ファイル形式バージョン（固定）

services:
  [service-name]:                # サービス名（rpi-wol, pc-power など）
    image: <image-reference>     # ghcr.io イメージ参照（required）
                                  # Format: ghcr.io/shiomi680/power-on-{service}:{version-tag}
                                  # Examples:
                                  # - ghcr.io/shiomi680/power-on-rpi:v1.0.0 (production)
                                  # - ghcr.io/shiomi680/power-on-rpi:latest (development - not recommended)

    ports:
      - "<host-port>:<container-port>"  # ポート・マッピング（required）
                                        # Examples:
                                        # - "5000:5000" (rpi-wol)
                                        # - "5001:5001" (pc-power)

    environment:                  # 環境変数（required）
      - VAR_NAME=value           # .env ファイルから置換可能
                                  # または直接値を指定

    restart: unless-stopped       # Restart policy（required）

    healthcheck:                  # ヘルスチェック（required）
      test: ["CMD", "curl", "-f", "http://localhost:{port}/api/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

### オプション・フィールド

```yaml
services:
  [service-name]:
    container_name: custom-name   # コンテナ名（オプション）
    
    build:                         # ローカル・ビルド（開発時オプション）
      context: ./[service-dir]
      dockerfile: Dockerfile
      # Note: 本番環境では image を優先。build と image の併存時、
      #       docker compose はビルド結果を使用。
      #       本番では build を削除するか、image のみ指定すること。

    environment:
      - LOG_LEVEL=INFO            # ログレベル（オプション、デフォルト: INFO）
      - SHUTDOWN_TIMEOUT=60       # シャットダウンタイムアウト（pc-power のみ、秒）

    networks:                      # ネットワーク指定（オプション）
      - power-on-network          # 複数サービス間通信で使用

    privileged: false             # Privileged モード（デフォルト: false）
                                  # pc-power が実際のシャットダウンを行う場合のみ true

    # pid: "host"                 # Host PID namespace（pc-power のみ、advanced）
```

---

## Root docker-compose.yml 仕様

### サービス定義

```yaml
version: '3.8'

services:
  # Raspberry Pi WOL + Web UI
  rpi-wol:
    image: ghcr.io/shiomi680/power-on-rpi:v1.0.0
    container_name: power-on-rpi
    ports:
      - "5000:5000"
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5000
      - PC_ADDRESS=${PC_ADDRESS}              # .env から置換
      - PC_API_PORT=5001
      - PC_API_TIMEOUT=5
      - LOG_LEVEL=${LOG_LEVEL:-INFO}          # Default: INFO
      - WOL_TARGET_MAC=${WOL_TARGET_MAC}      # .env から置換
      - WOL_BROADCAST_IP=${WOL_BROADCAST_IP:-255.255.255.255}  # Default: broadcast
    networks:
      - power-on-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s

  # PC Power Management API
  pc-power:
    image: ghcr.io/shiomi680/power-on-pc:v1.0.0
    container_name: power-on-pc
    ports:
      - "5001:5001"
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5001
      - SHUTDOWN_TIMEOUT=${SHUTDOWN_TIMEOUT:-60}  # Default: 60 seconds
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    networks:
      - power-on-network
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/api/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
    # privileged: true  # Uncomment if actual shutdown is required

networks:
  power-on-network:
    driver: bridge
```

---

## Standalone docker-compose.yml 仕様（rpi-wol、pc-power）

### rpi-wol/docker-compose.yml

```yaml
version: '3.8'

services:
  rpi-wol:
    image: ghcr.io/shiomi680/power-on-rpi:v1.0.0
    container_name: power-on-rpi
    ports:
      - "5000:5000"
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5000
      - PC_ADDRESS=${PC_ADDRESS:-192.168.1.100}
      - PC_API_PORT=5001
      - PC_API_TIMEOUT=5
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
      - WOL_TARGET_MAC=${WOL_TARGET_MAC}
      - WOL_BROADCAST_IP=${WOL_BROADCAST_IP:-255.255.255.255}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5000/api/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

### pc-power/docker-compose.yml

```yaml
version: '3.8'

services:
  pc-power:
    image: ghcr.io/shiomi680/power-on-pc:v1.0.0
    container_name: power-on-pc
    ports:
      - "5001:5001"
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5001
      - SHUTDOWN_TIMEOUT=${SHUTDOWN_TIMEOUT:-60}
      - LOG_LEVEL=${LOG_LEVEL:-INFO}
    restart: unless-stopped
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:5001/api/health"]
      interval: 30s
      timeout: 3s
      retries: 3
      start_period: 5s
```

---

## 環境変数参照仕様

### .env ファイル との連携

```bash
# .env ファイルで定義された変数が docker-compose.yml に ${VAR_NAME} として置換される

# .env.example または .env ファイルの例:
PC_ADDRESS=192.168.1.100
WOL_TARGET_MAC=00:11:22:33:44:55
WOL_BROADCAST_IP=255.255.255.255
FLASK_PORT=5000
LOG_LEVEL=INFO
SHUTDOWN_TIMEOUT=60

# docker-compose.yml での参照:
environment:
  - PC_ADDRESS=${PC_ADDRESS}            # .env で必ず定義必須
  - WOL_TARGET_MAC=${WOL_TARGET_MAC}    # .env で必ず定義必須
  - LOG_LEVEL=${LOG_LEVEL:-INFO}        # .env で未定義の場合、デフォルト: INFO
```

### 環境変数の必須性・デフォルト値

| 変数名 | 必須 | デフォルト値 | 説明 |
|--------|------|------------|------|
| PC_ADDRESS | Yes | — | PC のネットワーク・アドレス（環境固有） |
| WOL_TARGET_MAC | Yes | — | Wake-On-LAN 対象 MAC アドレス（環境固有） |
| WOL_BROADCAST_IP | No | 255.255.255.255 | WOL ブロードキャスト・アドレス |
| FLASK_PORT | No | 5000 | Flask サーバーのポート |
| LOG_LEVEL | No | INFO | ログ・レベル（DEBUG、INFO、WARNING、ERROR） |
| SHUTDOWN_TIMEOUT | No | 60 | シャットダウン・タイムアウト（秒、pc-power のみ） |

---

## バージョン・タグ戦略

### Release Assets 内の docker-compose.yml

**動作**: GitHub Actions で release asset に含まれる docker-compose.yml は、**release tag と同じバージョンをピン指定** している

```yaml
# release tag: v1.0.0 の場合
# GitHub Actions が release asset に含める docker-compose.yml:

services:
  rpi-wol:
    image: ghcr.io/shiomi680/power-on-rpi:v1.0.0  # Pinned!

  pc-power:
    image: ghcr.io/shiomi680/power-on-pc:v1.0.0   # Pinned!
```

### Repository の docker-compose.yml

**動作**: git リポジトリ内の docker-compose.yml は、最新（または開発） version を使用することが多い

```yaml
# Repo の docker-compose.yml（開発用）:

services:
  rpi-wol:
    image: ghcr.io/shiomi680/power-on-rpi:latest   # または最新 semantic tag

  pc-power:
    image: ghcr.io/shiomi680/power-on-pc:latest    # または最新 semantic tag
```

**Note**: Release assets と repository の docker-compose.yml が異なる可能性がある。Release download で本番安定性、git clone で最新開発バージョンを提供。

---

## 検証・テスト・シナリオ

### シナリオ 1: Release Download Path

```bash
# 1. Release assets から docker-compose.yml をダウンロード
curl -L -o docker-compose.yml \
  https://github.com/shiomi680/power-on/releases/download/v1.0.0/docker-compose.yml

# 2. docker-compose.yml の image tag が v1.0.0 であることを確認
grep "image:" docker-compose.yml
# Expected: image: ghcr.io/shiomi680/power-on-rpi:v1.0.0

# 3. イメージ・プル + コンテナ起動
docker compose pull
docker compose up -d

# 4. サービスがバージョン v1.0.0 で起動していることを確認
docker ps
docker logs power-on-rpi | grep "version"
```

### シナリオ 2: Git Clone Path

```bash
# 1. リポジトリをクローン
git clone https://github.com/shiomi680/power-on.git
cd power-on

# 2. docker-compose.yml が存在することを確認
ls docker-compose.yml

# 3. イメージ・プル + コンテナ起動
docker compose pull
docker compose up -d

# 4. ヘルスチェック検証
curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
```

---

## エラー・ハンドリング

### よくあるエラーと対処法

#### エラー 1: docker-compose: command not found

**原因**: docker-compose がインストールされていない

**対処法**:
```bash
# Docker Desktop には Docker Compose v2 が統合
docker compose version

# または docker-compose コマンドをインストール
# Ubuntu/Debian: sudo apt-get install docker-compose
# macOS: brew install docker-compose
```

#### エラー 2: port already in use

**原因**: ポート 5000 または 5001 が既に使用中

**対処法**:
```bash
# ポート 5000 の使用状況確認
lsof -i :5000

# または docker-compose.yml でポート番号を変更
# ports:
#   - "5002:5000"  # Host 5002 にマッピング
```

#### エラー 3: image not found

**原因**: ghcr.io からイメージを取得できない

**対処法**:
```bash
# インターネット接続確認
ping ghcr.io

# Docker daemon に ghcr.io 認証がある場合
docker login ghcr.io

# イメージを手動プル
docker pull ghcr.io/shiomi680/power-on-rpi:v1.0.0
```

---

## ベストプラクティス

1. **バージョン・ピンニング**: 本番環境では常に明確なバージョン・タグ（v1.0.0）を使用。latest は開発・テストのみ。
2. **環境変数分離**: PC_ADDRESS、WOL_TARGET_MAC などの環境固有値は .env ファイルに分離。
3. **ヘルスチェック**: すべてのサービスに healthcheck を定義。
4. **ネットワーク分離**: 複数サービス間通信が必要な場合、networks を定義。
5. **リスタート・ポリシー**: 本番環境では restart: unless-stopped を使用。
6. **ログ確認**: デプロイメント後は docker logs でサービス状況を確認。

