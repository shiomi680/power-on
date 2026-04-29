# コントラクト: GitHub Actions Release Automation ワークフロー

**日付**: 2026-04-29  
**対象**: `.github/workflows/release.yml`

## ワークフロー定義

GitHub Actions ワークフローは、新しい git tag（v*.*.* 形式）を作成・push した時に自動実行され、GitHub Release を作成し、release assets に docker-compose.yml と .env.example を自動含める。

---

## ワークフロー仕様

### ファイル位置

```
.github/workflows/release.yml
```

### トリガー条件

```yaml
on:
  push:
    tags:
      - 'v*'              # Semantic version tag のみトリガー
                          # Examples: v1.0.0, v1.0.0-rc1, v1.0.0-alpha
```

### ジョブ定義

```yaml
jobs:
  create-release:
    runs-on: ubuntu-latest
    
    steps:
      # Step 1: ソースコードをチェックアウト
      - uses: actions/checkout@v3
        with:
          fetch-depth: 0    # すべての履歴を取得（リリース・ノート生成用）

      # Step 2: Release を作成 + Assets をアップロード
      - uses: softprops/action-gh-release@v1
        with:
          files: |
            docker-compose.yml
            .env.example
          generate_release_notes: true    # GitHub が自動的にリリース・ノートを生成
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
```

---

## 詳細仕様

### Step 1: Checkout

**目的**: git tag に対応するソースコードをチェックアウト

```yaml
- uses: actions/checkout@v3
  with:
    fetch-depth: 0    # すべての git 履歴を取得
                      # リリース・ノート自動生成に必要
```

**出力**:
- ワーキング・ディレクトリに tag に対応するソースコード
- docker-compose.yml、.env.example、その他ファイルが利用可能

### Step 2: GitHub Release 作成 + Assets アップロード

**目的**: GitHub Release を作成し、release assets に docker-compose.yml と .env.example を自動含める

```yaml
- uses: softprops/action-gh-release@v1
  with:
    files: |
      docker-compose.yml        # Root の docker-compose.yml
      .env.example              # Root の .env.example
    
    generate_release_notes: true  # GitHub が自動的にリリース・ノートを生成
                                 # 前回のリリース以降の commits を要約
    
    draft: false                # Draft release ではなく、公開 release
    prerelease: false           # Pre-release ではなく、正式リリース
                                # v1.0.0-rc1、v1.0.0-alpha の場合は true に自動設定推奨
  
  env:
    GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}  # GitHub Actions の default token
```

**出力**:
- GitHub Release page に新しいリリースが作成される
- Release tag: v1.0.0（git tag から自動派生）
- Release assets に docker-compose.yml と .env.example が自動アップロード
- Release notes が自動生成される（前回リリース以降の変更を要約）

---

## ワークフロー実行例

### 実行フロー

```
Developer: git tag v1.0.0 && git push origin v1.0.0
  ↓
GitHub: v1.0.0 tag 受信
  ↓
GitHub Actions: release.yml workflow 自動トリガー
  ↓
Step 1: actions/checkout@v3
  - v1.0.0 tag に対応するソースコードをチェックアウト
  ↓
Step 2: softprops/action-gh-release@v1
  - GitHub Release を作成（tag: v1.0.0）
  - docker-compose.yml をアップロード
  - .env.example をアップロード
  - リリース・ノートを自動生成
  ↓
Result: https://github.com/shiomi680/power-on/releases/v1.0.0
  - docker-compose.yml (download link)
  - .env.example (download link)
  - Release notes (自動生成)
```

### ユーザー観点での利用フロー

```
User: GitHub Releases page (v1.0.0) を訪問
  ↓
User: Assets セクションで以下をダウンロード:
  - docker-compose.yml
  - .env.example
  ↓
User: ローカルで .env を設定
  ↓
User: docker compose up -d でシステム起動
```

---

## Release Assets の内容仕様

### docker-compose.yml

**バージョン・ピンニング規則**:
- Release assets に含まれる docker-compose.yml は、**release tag と同じバージョンをピン指定**

```yaml
# v1.0.0 tag を push した場合、
# GitHub Actions が v1.0.0 release assets に含める docker-compose.yml:

services:
  rpi-wol:
    image: ghcr.io/shiomi680/power-on-rpi:v1.0.0  # Pinned to v1.0.0!

  pc-power:
    image: ghcr.io/shiomi680/power-on-pc:v1.0.0   # Pinned to v1.0.0!
```

**実装方法**:
1. git repository の docker-compose.yml で最新版を管理
2. Release assets には、リリース時点で repository にある docker-compose.yml がそのままコピーされる
3. Repository の docker-compose.yml が既に image tag を v1.0.0 に設定していることを確認

**または**、GitHub Actions で動的に docker-compose.yml を修正：

```yaml
# Advanced: docker-compose.yml の image tag を動的に置換
- name: Update docker-compose.yml with release tag
  run: |
    VERSION=${GITHUB_REF#refs/tags/}  # v1.0.0
    sed -i "s/:latest/:$VERSION/g" docker-compose.yml
    # :latest を :v1.0.0 に置換

- uses: softprops/action-gh-release@v1
  with:
    files: |
      docker-compose.yml    # 置換後のファイル
      .env.example
```

### .env.example

**内容**: デフォルト値を含む環境変数テンプレート

```bash
# .env.example
PC_ADDRESS=192.168.1.100
WOL_TARGET_MAC=aa:bb:cc:dd:ee:ff
WOL_BROADCAST_IP=255.255.255.255
FLASK_PORT=5000
LOG_LEVEL=INFO
SHUTDOWN_TIMEOUT=60
```

**ユーザーの利用**:
```bash
curl -O https://github.com/shiomi680/power-on/releases/download/v1.0.0/.env.example
cp .env.example .env
# .env を編集（PC_ADDRESS、WOL_TARGET_MAC は必須）
```

---

## 実装例（完全なワークフロー）

### `.github/workflows/release.yml`

```yaml
name: Create Release

on:
  push:
    tags:
      - 'v*'            # Trigger on semantic version tags (v1.0.0, v1.0.0-rc1, etc.)

jobs:
  create-release:
    runs-on: ubuntu-latest
    
    steps:
      - name: Checkout code
        uses: actions/checkout@v3
        with:
          fetch-depth: 0
      
      - name: Determine pre-release flag
        id: pre_release
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          if [[ $TAG =~ -rc|-alpha|-beta ]]; then
            echo "is_prerelease=true" >> $GITHUB_OUTPUT
          else
            echo "is_prerelease=false" >> $GITHUB_OUTPUT
          fi
      
      - name: Create Release with Assets
        uses: softprops/action-gh-release@v1
        with:
          files: |
            docker-compose.yml
            .env.example
          generate_release_notes: true
          draft: false
          prerelease: ${{ steps.pre_release.outputs.is_prerelease }}
        env:
          GITHUB_TOKEN: ${{ secrets.GITHUB_TOKEN }}
      
      - name: Release created successfully
        run: |
          TAG=${GITHUB_REF#refs/tags/}
          echo "✓ Release $TAG created successfully"
          echo "✓ Assets: docker-compose.yml, .env.example"
          echo "Release URL: https://github.com/${{ github.repository }}/releases/tag/$TAG"
```

---

## 検証・テスト

### 実行前チェック

```bash
# 1. Docker-compose ファイルが存在することを確認
ls -la docker-compose.yml

# 2. .env.example が存在することを確認
ls -la .env.example

# 3. github/workflows/release.yml が存在することを確認
ls -la .github/workflows/release.yml

# 4. Git remote が設定されていることを確認
git remote -v
```

### リリース実行手順

```bash
# 1. ローカルで semantic version tag を作成
git tag v1.0.0

# 2. Tag を push（GitHub Actions 自動トリガー）
git push origin v1.0.0

# 3. GitHub Actions の実行を確認
# GitHub UI: Actions → Create Release → workflow を確認

# 4. Release page で assets が自動アップロードされたことを確認
# GitHub UI: Releases → v1.0.0 → Assets セクション
#   - docker-compose.yml (download link)
#   - .env.example (download link)

# 5. Release notes が自動生成されたことを確認
# Release page: Releases notes セクション
```

### ダウンロード検証

```bash
# Release assets を curl でダウンロード
curl -L -o /tmp/docker-compose.yml \
  https://github.com/shiomi680/power-on/releases/download/v1.0.0/docker-compose.yml

curl -L -o /tmp/.env.example \
  https://github.com/shiomi680/power-on/releases/download/v1.0.0/.env.example

# ファイルが正しくダウンロードされたことを確認
ls -la /tmp/docker-compose.yml
ls -la /tmp/.env.example

# docker-compose.yml が有効な YAML であることを確認
docker-compose config -f /tmp/docker-compose.yml

# Image tag がバージョンと一致していることを確認
grep "image:" /tmp/docker-compose.yml | grep "v1.0.0"
# Expected:
# image: ghcr.io/shiomi680/power-on-rpi:v1.0.0
# image: ghcr.io/shiomi680/power-on-pc:v1.0.0
```

---

## トラブルシューティング

### エラー 1: Workflow が実行されない

**原因**: Tag が semantic version パターン（v*.*.* ）に一致していない

**対処法**:
```bash
# 正しいフォーマット
git tag v1.0.0          # ✓ OK
git tag v1.0.0-rc1      # ✓ OK (pre-release)

# 間違ったフォーマット
git tag 1.0.0           # ✗ NG (v がない)
git tag release-1.0.0   # ✗ NG (v がない)
```

### エラー 2: Assets が自動アップロードされない

**原因**: ファイルが git リポジトリに存在しない、または `.gitignore` で除外されている

**対処法**:
```bash
# ファイルが git に追跡されていることを確認
git ls-files | grep -E "docker-compose.yml|.env.example"

# または git add
git add docker-compose.yml .env.example
git commit -m "Add docker-compose and env template"
```

### エラー 3: Release notes が生成されない

**原因**: `fetch-depth: 0` が設定されていない

**対処法**:
```yaml
- uses: actions/checkout@v3
  with:
    fetch-depth: 0    # 重要: すべての履歴を取得
```

---

## ベストプラクティス

1. **Semantic Versioning**: 常に v*.*.* 形式のタグを使用（例: v1.0.0、v1.0.1、v2.0.0）
2. **Pre-release マーク**: Release candidates、alpha、beta には -rc1、-alpha、-beta を付与（例: v1.0.0-rc1）
3. **Release Notes**: GitHub が自動生成するため、コミット・メッセージは明確に
4. **バージョン・ピンニング**: Release assets の docker-compose.yml は release tag と同じバージョンをピン指定
5. **テスト・リリース**: v0.1.0-alpha など試験的リリースで workflow をテスト

