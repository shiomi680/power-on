# CI/CD パイプライン ガイド

GitHub Actions で Docker イメージを自動ビルド・テスト・ghcr.io へのデプロイを行います。

## 📋 ワークフロー概要

```
Code Push
    ↓
GitHub Actions (CI)
    ├─ テスト実行 (pytest)
    ├─ Docker イメージビルド
    └─ ghcr.io へプッシュ
         ↓
    本番環境
    (docker pull で最新イメージを取得)
```

## 🔧 セットアップ

### 1. GitHub リポジトリ設定

#### レジストリアクセス権限の確認

GitHub Actions で ghcr.io にプッシュするには、以下を確認:

1. **リポジトリ設定** → **Actions** → **General**
   - "Read and write permissions" を有効化
   - "Allow GitHub Actions to create and approve pull requests" （オプション）

2. **Package settings**
   - リポジトリが public の場合、誰でも pull 可能
   - private の場合、アクセス権限のあるユーザーのみ可能

### 2. ワークフロー実行確認

```bash
# ワークフローを確認
git log --oneline | head -1

# GitHub UI で以下にアクセス
# https://github.com/your-repo/power-on/actions
```

## 📦 イメージの取得

### ghcr.io からのプル

```bash
# Raspberry Pi
docker pull ghcr.io/your-username/power-on/power-on-rpi:latest
docker pull ghcr.io/your-username/power-on/power-on-rpi:main

# PC
docker pull ghcr.io/your-username/power-on/power-on-pc:latest
docker pull ghcr.io/your-username/power-on/power-on-pc:main
```

### バージョン指定でのプル

```bash
# セマンティックバージョニング
docker pull ghcr.io/your-username/power-on/power-on-rpi:v1.0.0
docker pull ghcr.io/your-username/power-on/power-on-rpi:v1.0

# ブランチ指定
docker pull ghcr.io/your-username/power-on/power-on-rpi:001-pc-power-control-abc1234
```

## 🚀 本番環境でのデプロイ

### Raspberry Pi

```bash
cd ~/power-on/rpi-wol

# イメージをプル
docker pull ghcr.io/your-username/power-on/power-on-rpi:latest

# docker-compose.yml を修正（オプション）
# イメージを指定する場合
cat > docker-compose.override.yml << EOF
services:
  rpi-wol:
    image: ghcr.io/your-username/power-on/power-on-rpi:latest
EOF

# 実行
docker compose up -d
```

### PC

```bash
cd ~/power-on/pc-power

# イメージをプル
docker pull ghcr.io/your-username/power-on/power-on-pc:latest

# 実行
docker compose up -d
```

## 📊 ワークフロー詳細

### トリガー条件

```yaml
# 以下のイベントで自動実行
- main ブランチへの push
- 001-pc-power-control ブランチへの push
- v* タグの push（セマンティックバージョニング）
- Pull Request

# main ブランチの場合のみ ghcr.io へプッシュ
# PR の場合はテストのみ実行
```

### ジョブ

#### 1. Build and Push

```
✅ コード取得
✅ Docker Buildx セットアップ
✅ ghcr.io にログイン
✅ メタデータ抽出（タグ・ラベル）
✅ イメージビルド
✅ ghcr.io へプッシュ
✅ キャッシュ保存
```

#### 2. Test

```
✅ コード取得
✅ Python 3.10 セットアップ
✅ 依存パッケージ インストール
✅ pytest 実行
```

### タグ付けルール

| 条件 | タグ例 |
|------|--------|
| main ブランチ | `latest`, `main`, `sha-abc1234` |
| タグ push | `v1.0.0`, `v1.0`, `v1` |
| 機能ブランチ | `001-pc-power-control`, `001-pc-power-control-sha-abc1234` |

## 📈 ワークフロー実行状況の確認

### GitHub UI

```
https://github.com/your-username/power-on/actions
```

各ワークフロー実行をクリックして詳細を確認。

### コマンドライン

```bash
# ワークフロー一覧
gh workflow list

# 最新の実行結果
gh run list --workflow=docker-publish.yml

# 特定の実行詳細
gh run view <run-id>

# ログ取得
gh run view <run-id> --log
```

## 🔐 セキュリティ

### GitHub Token について

- **GITHUB_TOKEN**: GitHub Actions が自動生成
  - リポジトリ限定のアクセス権限
  - ワークフロー内でのみ使用可能
  - 自動的にローテーション
  - セキュアで推奨

### ghcr.io へのアクセス

- **Public イメージ**: 認証なしで pull 可能
- **Private イメージ**: 認証が必要
  - `docker login ghcr.io -u <username> -p <token>`
  - Token は PAT（Personal Access Token）を使用

## 🐛 トラブルシューティング

### イメージがプッシュされない

```bash
# ワークフロー実行ログを確認
gh run view <run-id> --log

# チェック項目
1. リポジトリが public か確認
2. GitHub Actions 権限を確認
3. ブランチ名が正しいか確認
4. タグが正しい形式か確認（v* など）
```

### テストが失敗する

```bash
# ローカルでテスト実行
cd rpi-wol && pytest tests/ -v
cd pc-power && pytest tests/ -v
```

### イメージサイズが大きい

```bash
# Dockerfile の最適化
# - alpine ベースイメージ使用
# - 不要なレイヤー削除
# - マルチステージビルド活用

# キャッシュを確認
docker buildx du
```

## 📚 関連リンク

- [GitHub Actions ドキュメント](https://docs.github.com/ja/actions)
- [ghcr.io （GitHub Container Registry）](https://docs.github.com/en/packages/working-with-a-github-packages-registry/working-with-the-container-registry)
- [docker/metadata-action](https://github.com/docker/metadata-action)
- [docker/build-push-action](https://github.com/docker/build-push-action)

## 🔄 ワークフロー YAML

ワークフロー定義: `.github/workflows/docker-publish.yml`

主要な設定:

```yaml
# トリガー
on:
  push:
    branches: [main, 001-pc-power-control]
    tags: ['v*']
  pull_request:
    branches: [main]

# イメージ名
IMAGE_NAME_RPI: ${{ github.repository }}/power-on-rpi
IMAGE_NAME_PC: ${{ github.repository }}/power-on-pc

# 権限
permissions:
  packages: write  # ghcr.io へプッシュ可能

# ジョブ
jobs:
  build-and-push:
    # 複数コンポーネント対応（matrix ビルド）
  test:
    # Python テスト実行
```

## 📋 デプロイメント フロー（推奨）

```
1. ローカルでテスト
   $ make test

2. コミット＆プッシュ
   $ git commit -m "..."
   $ git push origin branch-name

3. GitHub Actions 実行
   自動テスト + イメージビルド

4. 本番環境でプル
   $ docker pull ghcr.io/.../power-on-rpi:latest
   $ docker compose up -d
```

---

**次回更新時**: ワークフローログを確認して、ビルド成功を確認してください。
