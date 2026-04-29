# Data Model: Deployment Automation

**作成日**: 2026-04-29  
**スコープ**: Docker イメージ、コンテナ、デプロイメント対象のデータ構造

## キーエンティティ

### 1. Docker イメージ

#### Entity: PowerOnRPIImage

Docker イメージ（Raspberry Pi コンポーネント）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `image_name` | String | `ghcr.io/{owner}/power-on/power-on-rpi` |
| `tags` | List[String] | `latest`, `main`, `v1.0.0`, `sha-abc123` |
| `base_image` | String | `python:3.10-slim` |
| `platform` | String | `linux/arm64` (for Raspberry Pi 4+) |
| `size_mb` | Integer | ~200 (実測) |
| `built_at` | DateTime | ビルド時刻 |
| `registry` | String | `ghcr.io` |

**ビルド入力**:
- `rpi-wol/Dockerfile`
- `rpi-wol/src/**/*.py`
- `rpi-wol/requirements.txt`
- `rpi-wol/templates/`, `rpi-wol/static/`

**検証**:
- pytest テスト全体がパス
- イメージ起動時にポート 5000 でリッスン可能
- `/api/health` エンドポイント応答

#### Entity: PowerOnPCImage

Docker イメージ（PC コンポーネント）

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `image_name` | String | `ghcr.io/{owner}/power-on/power-on-pc` |
| `tags` | List[String] | `latest`, `main`, `v1.0.0`, `sha-abc123` |
| `base_image` | String | `python:3.10-slim` |
| `platform` | String | `linux/amd64`, `linux/arm64` |
| `size_mb` | Integer | ~180 (実測) |
| `built_at` | DateTime | ビルド時刻 |
| `registry` | String | `ghcr.io` |

**ビルド入力**:
- `pc-power/Dockerfile`
- `pc-power/src/**/*.py`
- `pc-power/requirements.txt`

**検証**:
- pytest テスト全体がパス
- イメージ起動時にポート 5001 でリッスン可能
- `/api/health` エンドポイント応答

---

### 2. Docker Compose 構成

#### Entity: RaspberryPiComposition

Raspberry Pi 本番デプロイメント用の Docker Compose 設定

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `compose_file` | String | `rpi-wol/docker-compose.yml` |
| `services` | Dict | rpi-wol サービス定義 |
| `networks` | List[String] | 外部ネットワーク（必要に応じて） |
| `env_file` | String | `.env` から環境変数読み込み |
| `env_vars` | Dict | PC_ADDRESS, WOL_TARGET_MAC, LOG_LEVEL など |
| `ports` | List[String] | `5000:5000` (Web UI) |
| `restart_policy` | String | `always` |

**環境変数スキーマ**:
```
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
PC_ADDRESS=<PC の IP または hostname>
PC_API_PORT=5001
PC_API_TIMEOUT=5
WOL_TARGET_MAC=aa:bb:cc:dd:ee:ff
WOL_BROADCAST_IP=255.255.255.255
LOG_LEVEL=INFO
```

**ヘルスチェック**:
- コマンド: `curl http://localhost:5000/api/health`
- インターバル: 30秒
- タイムアウト: 5秒
- 初期遅延: 10秒

#### Entity: PCComposition

PC 本番デプロイメント用の Docker Compose 設定

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `compose_file` | String | `pc-power/docker-compose.yml` |
| `services` | Dict | pc-power サービス定義 |
| `networks` | List[String] | ローカルネットワーク |
| `env_file` | String | `.env` から環境変数読み込み |
| `env_vars` | Dict | SHUTDOWN_TIMEOUT, LOG_LEVEL など |
| `ports` | List[String] | `5001:5001` (API) |
| `restart_policy` | String | `always` |
| `privileged` | Boolean | `true` (シャットダウンコマンド実行) |

**環境変数スキーマ**:
```
FLASK_HOST=0.0.0.0
FLASK_PORT=5001
SHUTDOWN_TIMEOUT=60
LOG_LEVEL=INFO
```

---

### 3. GitHub Actions ワークフロー

#### Entity: DockerPublishWorkflow

GitHub Actions CI/CD パイプライン定義

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `workflow_file` | String | `.github/workflows/docker-publish.yml` |
| `trigger_events` | List[String] | `push` (main, 001-pc-power-control), `pull_request` (main), tags (v*) |
| `jobs` | List[String] | `build-and-push`, `test` |
| `matrix_strategy` | Dict | rpi-wol と pc-power の並列ビルド |
| `registry` | String | `ghcr.io` |
| `auth_method` | String | GITHUB_TOKEN (自動) |

**ジョブ: build-and-push**

マトリックス設定:
```yaml
matrix:
  - component: rpi-wol
    image_name: power-on-rpi
  - component: pc-power
    image_name: power-on-pc
```

ステップ:
1. Checkout code (actions/checkout@v4)
2. Set up Docker Buildx (docker/setup-buildx-action@v3)
3. Log in to Container Registry (docker/login-action@v3)
4. Extract metadata (docker/metadata-action@v5)
5. Build and push Docker image (docker/build-push-action@v5)

**タグ付けメタデータ**:
- ref (branch): main → `main`, feature → `<branch-name>`
- semver (tag): v1.0.0 → `v1.0.0`, `v1.0`, `v1`
- sha: すべてのイベント → `<branch>-sha-<commit>`
- latest: main ブランチのみ → `latest`

**ジョブ: test**

マトリックス設定:
```yaml
matrix:
  component:
    - rpi-wol
    - pc-power
```

ステップ:
1. Checkout code
2. Set up Python 3.10
3. Install dependencies (requirements.txt)
4. Run pytest (tests/ -v)

**実行条件**: push + PR どちらのイベントでも実行

---

### 4. デプロイメント成果物

#### Entity: RegistryEntry

ghcr.io に保存されたイメージエントリ

| フィールド | 型 | 説明 |
|-----------|-----|------|
| `registry_url` | String | `ghcr.io/{owner}/power-on/{image_name}:{tag}` |
| `image_digest` | String | SHA256 ハッシュ |
| `pushed_at` | DateTime | プッシュ時刻 |
| `accessible_from` | String | Public (リポジトリが public の場合) |

---

## 関連性

```
GitHub Action ワークフロー
  ├─ rpi-wol Dockerfile
  │   └─ PowerOnRPIImage
  │       └─ ghcr.io/*/power-on-rpi:tag (RegistryEntry)
  │           ↓ docker pull
  │           RaspberryPiComposition (docker-compose up)
  │               ↓
  │               Web UI (port 5000)
  │
  └─ pc-power Dockerfile
      └─ PowerOnPCImage
          └─ ghcr.io/*/power-on-pc:tag (RegistryEntry)
              ↓ docker pull
              PCComposition (docker-compose up)
                  ↓
                  API Server (port 5001)
```

---

## 状態遷移

### イメージライフサイクル

```
コード変更
  ↓
GitHub Actions トリガー
  ↓
テスト実行 (PASS/FAIL)
  ↓[FAIL]→ 通知
  ↓[PASS]
イメージビルド
  ↓
ghcr.io プッシュ (push イベントのみ)
  ↓
本番環境で docker pull で利用可能
```

### コンテナライフサイクル

```
docker compose up -d
  ↓
コンテナ起動 (< 30秒)
  ↓
ヘルスチェック開始 (10秒後から定期実行)
  ↓
healthy ステータス
  ↓
リクエスト処理
```
