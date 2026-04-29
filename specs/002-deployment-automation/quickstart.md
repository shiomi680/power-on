# Quickstart: Docker Deployment

**作成日**: 2026-04-29  
**対象者**: 開発者、運用者  
**目的**: Docker コンテナでのローカル開発とコンテナレジストリからの本番デプロイメント

---

## シナリオ 1: ローカル開発環境での両コンポーネント同時実行

**目的**: ローカルマシンで Web UI と API を同時実行してテスト

### 前提条件

- Docker 20.10+
- Docker Compose V2
- Python 3.10+
- リポジトリをクローン

### 手順

#### 1. イメージビルド

```bash
cd /path/to/power-on
docker compose build
```

**実行結果**: 両コンポーネントのイメージが docker イメージレジストリに作成される

#### 2. コンテナ起動

```bash
docker compose up -d
```

**実行結果**: 
- `rpi-wol` コンテナ: ポート 5000 でリッスン
- `pc-power` コンテナ: ポート 5001 でリッスン

#### 3. 動作確認

**Web UI へのアクセス**:
```bash
curl http://localhost:5000
# ブラウザで http://localhost:5000 を開く
```

**API ヘルスチェック**:
```bash
curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
# どちらも {"status": "ok"} を返す
```

**コンテナ状態確認**:
```bash
docker ps
# 両コンテナの STATUS が Up で、HEALTHCHECK が healthy を示す
```

#### 4. 環境変数カスタマイズ（オプション）

`.env` ファイルをルートディレクトリに作成して環境変数を設定：

```bash
cat > .env << EOF
WOL_TARGET_MAC=aa:bb:cc:dd:ee:ff
WOL_BROADCAST_IP=255.255.255.255
SHUTDOWN_TIMEOUT=60
LOG_LEVEL=DEBUG
EOF

docker compose up -d --force-recreate
```

---

## シナリオ 2: Raspberry Pi への本番デプロイ

**目的**: Raspberry Pi に Web UI + WOL サービスをデプロイ

### 前提条件

- Raspberry Pi (4 以上推奨)
- Docker + Docker Compose V2 インストール済み
- ターゲット PC の MAC アドレスを把握
- ターゲット PC の IP アドレスまたはホスト名

### 手順

#### 1. リポジトリクローン

```bash
ssh pi@<raspberry-pi-ip>

cd ~
git clone https://github.com/<owner>/power-on.git
cd power-on/rpi-wol
```

#### 2. 環境変数設定

```bash
cp .env.example .env
nano .env

# 以下を編集:
# PC_ADDRESS=<PC の IP または hostname>
# WOL_TARGET_MAC=<PC の MAC アドレス>
```

例:
```bash
cat > .env << EOF
FLASK_HOST=0.0.0.0
FLASK_PORT=5000
PC_ADDRESS=192.168.1.50
PC_API_PORT=5001
PC_API_TIMEOUT=5
WOL_TARGET_MAC=aa:bb:cc:dd:ee:ff
WOL_BROADCAST_IP=255.255.255.255
LOG_LEVEL=INFO
EOF
```

#### 3. イメージ取得（オプション: 自分でビルドするか ghcr.io から pull か）

**オプション A: GitHub Container Registry から最新イメージを pull**

```bash
docker pull ghcr.io/<owner>/power-on/power-on-rpi:latest
docker compose up -d
```

**オプション B: ローカルビルド**

```bash
docker compose build
docker compose up -d
```

#### 4. 起動確認

```bash
docker ps
docker logs rpi-wol

# ブラウザで http://<raspberry-pi-ip>:5000 にアクセス
```

#### 5. 自動再起動設定（オプション）

```bash
docker compose up -d --restart-policy always
```

---

## シナリオ 3: PC への本番デプロイ

**目的**: PC に電源管理 API をデプロイ

### 前提条件

- Windows/Linux PC
- Docker + Docker Compose V2 インストール済み
- Raspberry Pi からのネットワーク通信可能

### 手順

#### 1. リポジトリクローン

```bash
cd <deployment-directory>
git clone https://github.com/<owner>/power-on.git
cd power-on/pc-power
```

#### 2. 環境変数設定

```bash
cp .env.example .env
# 編集不要（デフォルト値で OK）
```

#### 3. イメージ取得

```bash
# GitHub Container Registry から最新イメージを pull
docker pull ghcr.io/<owner>/power-on/power-on-pc:latest
docker compose up -d
```

#### 4. 起動確認

```bash
docker ps
docker logs pc-power

# API ヘルスチェック
curl http://localhost:5001/api/health
```

---

## シナリオ 4: GitHub Actions CI/CD パイプラインの実行

**目的**: コード変更時にワークフローが自動実行されることを確認

### トリガーイベント

| イベント | 処理 |
|---------|------|
| `main` ブランチへの push | テスト実行 → イメージビルド → ghcr.io プッシュ |
| `001-pc-power-control` ブランチへの push | テスト実行 → イメージビルド → ghcr.io プッシュ |
| Pull Request (→ main) | テスト実行のみ |
| `v*` タグ push | テスト実行 → イメージビルド → ghcr.io にセマンティックバージョニング対応プッシュ |

### 確認手順

1. **コード変更とプッシュ**:
```bash
git commit -m "小さな変更"
git push origin 001-pc-power-control
```

2. **GitHub UI でワークフロー実行確認**:
```
https://github.com/<owner>/power-on/actions
```

3. **ログ確認**:
```bash
gh run list --workflow=docker-publish.yml

# 特定の実行詳細
gh run view <run-id>

# ログ取得
gh run view <run-id> --log
```

4. **イメージプッシュ確認**:
```bash
# ghcr.io で新しいイメージを確認
docker pull ghcr.io/<owner>/power-on/power-on-rpi:latest

# イメージ情報表示
docker image ls | grep power-on
```

---

## シナリオ 5: バージョンタグ付きリリース

**目的**: セマンティックバージョニングでリリースイメージを作成

### 手順

```bash
# リリース対象のコミットにタグを作成
git tag v1.0.0

# リモートにプッシュ
git push origin v1.0.0
```

### ワークフロー自動処理

タグ push により以下が自動実行:
- テスト実行
- イメージビルド
- ghcr.io に複数タグでプッシュ: `v1.0.0`, `v1.0`, `v1`

**確認**:
```bash
# ghcr.io で複数タグが存在することを確認
docker pull ghcr.io/<owner>/power-on/power-on-rpi:v1.0.0
docker pull ghcr.io/<owner>/power-on/power-on-rpi:v1.0
docker pull ghcr.io/<owner>/power-on/power-on-rpi:v1
```

---

## トラブルシューティング

### コンテナが起動しない

```bash
# ログを確認
docker compose logs -f rpi-wol

# ポート競合確認
lsof -i :5000
lsof -i :5001

# 強制リスタート
docker compose down -v
docker compose up -d
```

### ワークフローが失敗する

```bash
# GitHub UI でエラーメッセージを確認
# または
gh run view <run-id> --log | less
```

### イメージ pull が失敗する

```bash
# 認証確認（private リポジトリの場合）
docker login ghcr.io -u <username> -p <token>

# イメージ存在確認
curl https://ghcr.io/v2/<owner>/power-on/power-on-rpi/tags/list
```

---

## 次のステップ

- **運用ガイド**: `docs/DOCKER.md` を参照して詳細なオプションを確認
- **CI/CD 詳細**: `docs/CI-CD.md` でワークフロー内容を理解
- **統合デプロイメント**: `docs/DEPLOYMENT.md` で全体アーキテクチャを確認
