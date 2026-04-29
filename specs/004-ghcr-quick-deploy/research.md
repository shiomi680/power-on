# 研究フェーズ: ghcr.io ワンコマンド・デプロイメント

**日付**: 2026-04-29  
**入力**: plan.md Phase 0 の主要質問への回答

## 1. docker-compose.yml 利用パターン

### 質問
git リポジトリに docker-compose.yml を保管・管理し、ユーザーが git clone してそのまま使用可能にするには？

### 決定
**Simple Strategy (Pattern 1)**:
- **Single Source of Truth**: git リポジトリの docker-compose.yml
- **ユーザーの利用方法**: git clone → .env 設定 → docker compose up
- **Release assets**: docker-compose.yml は含含しない（複雑性回避）

### 根拠
1. **シンプル性**: 複雑な自動化なし、ファイルは 1 箇所で管理
2. **保守性**: docker-compose.yml は git repo でのみ管理
3. **明確性**: ユーザーは git clone で完全なコンテキスト（README、Dockerfile 等）を入手可能
4. **業界標準**: 多くのオープン・ソース・プロジェクトがこのアプローチを採用

### 実装パターン

**リポジトリ構造**:
```
repo-root/
├── README.md                    # Deployment guide
├── docker-compose.yml           # Single source of truth
├── rpi-wol/docker-compose.yml   # Standalone (rpi-only)
├── pc-power/docker-compose.yml  # Standalone (pc-only)
└── .env.example                 # Default environment variables
```

**Root docker-compose.yml 例**:
```yaml
version: '3.8'
services:
  rpi-wol:
    image: ghcr.io/shiomi680/power-on-rpi:v1.0.0  # Pinned version
    # ... config
  pc-power:
    image: ghcr.io/shiomi680/power-on-pc:v1.0.0   # Pinned version
    # ... config
```

---

## 2. デプロイメント・ドキュメント構造

### 質問
初心者向けに明確な git clone → docker compose up フロー、README での手順説明はどうするか？

### 決定
**README.md に段階的なクイックスタート・セクション記載**

```markdown
# クイックスタート - 5分でデプロイ

**必須**: Docker v20.10+、git

## ステップ 1: リポジトリをクローン
git clone https://github.com/shiomi680/power-on
cd power-on

## ステップ 2: 環境を設定
cp .env.example .env
# PC_ADDRESS、WOL_TARGET_MAC を環境に応じて編集
nano .env

## ステップ 3: docker compose で起動
docker compose up -d

## ステップ 4: ヘルスチェック
curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
```

### 根拠
1. **初心者向け**: 段階的な手順で理解しやすい
2. **自動性**: コピペで動作するコマンド
3. **検証**: ヘルスチェックで成功確認可能
4. **完全性**: すべての必須情報を 1 つのセクションで提供

---

## 3. バージョン・ピン指定・戦略

### 質問
docker-compose.yml でバージョン・ピン指定、.env.example の環境変数デフォルト値定義はどうするか？

### 決定

**docker-compose.yml**: 具体的バージョン・タグをピン指定
```yaml
services:
  rpi-wol:
    image: ghcr.io/shiomi680/power-on-rpi:v1.0.0  # Pinned version
  pc-power:
    image: ghcr.io/shiomi680/power-on-pc:v1.0.0   # Pinned version
```

**.env.example**: デフォルト値を含める
```bash
# .env.example
PC_ADDRESS=192.168.1.100        # 環境に応じて編集（必須）
WOL_TARGET_MAC=aa:bb:cc:dd:ee:ff # 環境に応じて編集（必須）
WOL_BROADCAST_IP=255.255.255.255  # デフォルト（通常不変）
FLASK_PORT=5000                    # デフォルト（通常不変）
LOG_LEVEL=INFO                     # デフォルト（通常不変）
SHUTDOWN_TIMEOUT=60                # デフォルト（通常不変）
```

**バージョン管理**:
- Repository の docker-compose.yml はバージョンをピン指定（v1.0.0）
- 新しいリリース時は docker-compose.yml を更新してから git tag を作成
- ユーザーが git clone した時点で使用中のバージョンが反映される

### 根拠
1. **再現性**: ピン指定で同じバージョンが起動される
2. **本番安定性**: バージョン・ピンで予測不可能な更新を防止
3. **開発フロー**: Repository は常に安定版のバージョンを指定

### 検証方法
```bash
# 1. git clone して docker-compose.yml を確認
git clone https://github.com/shiomi680/power-on
grep "image:" docker-compose.yml
# Expected: ghcr.io/shiomi680/power-on-rpi:v1.0.0

# 2. docker compose で起動
docker compose up -d

# 3. イメージバージョンが正しいことを確認
docker ps
docker inspect power-on-rpi | grep "Image"
```

---

## まとめ

| 項目 | 決定 |
|-----|------|
| docker-compose.yml 保管 | Git repository (single source of truth) |
| ユーザー取得方法 | git clone |
| Release assets | docker-compose.yml は含含しない |
| デプロイ・フロー | git clone → .env 設定 → docker compose up |
| バージョン・ピン指定 | Repository の docker-compose.yml は具体的バージョンをピン |
| シンプル性 | 複雑な自動化なし、手作業最小化 |

