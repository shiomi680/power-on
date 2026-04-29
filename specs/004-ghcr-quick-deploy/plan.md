# 実装計画: ghcr.io プリビルト・イメージ・ワンコマンド・デプロイメント

**ブランチ**: `004-ghcr-quick-deploy` | **日付**: 2026-04-29 | **仕様**: [specs/004-ghcr-quick-deploy/spec.md](spec.md)
**入力**: `/specs/004-ghcr-quick-deploy/spec.md` の機能仕様

## 概要

ghcr.io からのプリビルト・イメージを使用したワンコマンド・デプロイメント・ドキュメントを整備する。README.md を改善し、docker pull → docker compose up をデフォルト推奨方法として確立。git clone で docker-compose.yml を入手し、そのまま使用可能にすることで、初心者ユーザーの 2 分以内の起動、本番環境のバージョン・ピン指定による再現性が実現される。

## 技術コンテキスト

**形式**: Markdown ドキュメント  
**主要依存関係**: Docker (v20.10+)、docker-compose、ghcr.io (GitHub Container Registry)  
**ストレージ**: N/A（ドキュメント・デプロイメント）  
**テスト**: ドキュメント検証（コマンド実行可能性、明確性）  
**対象プラットフォーム**: GitHub README（公開ドキュメント）、git リポジトリ  
**プロジェクトタイプ**: ドキュメント更新  
**パフォーマンス目標**: 2 分以内にシステム起動（SC-002）  
**制約**: 初心者向け明確性、完全なコマンド例、バージョン管理  
**スコープ**: README.md クイックスタート・セクション修正・拡張

## 憲法チェック

*ゲート: フェーズ 0 研究前に合格必須。フェーズ 1 設計後に再確認。*

| 原則 | 状態 | 備考 |
|------|------|------|
| I. 日本語優先 | ✅ 合格 | ドキュメント・計画・コミットメッセージが日本語。技術用語（ghcr、Docker、github actions 等）は原語。 |
| II. ライブラリファースト | ⚠️ 非該当 | ドキュメント・自動化作業であり、新規ライブラリ作成ではない。 |
| III. CLI インターフェース | ⚠️ 非該当 | ドキュメント作業であり、CLI インターフェース作成ではない。 |
| IV. テスト優先 | ✅ 合格 | SC-001～SC-005 で測定可能なテスト基準を定義。docker pull・docker compose up が実行可能で検証。 |
| V. 統合テスト重視 | ✅ 合格 | docker pull + docker compose up のエンドツーエンド・デプロイメント検証。git clone + .env 設定 + docker compose up の統合検証。 |

**結果**: 合格 - ドキュメント+自動化作業で憲法違反なし。フェーズ 0 に進行。

## プロジェクト構造

### ドキュメント（本機能）

```text
specs/004-ghcr-quick-deploy/
├── plan.md              # このファイル
├── research.md          # フェーズ 0: docker-compose.yml 利用パターン、デプロイメント・ドキュメント構造、バージョン・ピン指定戦略
├── data-model.md        # フェーズ 1: デプロイメント・モデル（git clone ベース）
├── quickstart.md        # フェーズ 1: ワンコマンド・デプロイメント・シナリオ（3パス：git clone、バージョン・ピン、ローカル・ビルド）
├── contracts/           # フェーズ 1: docker-compose.yml コントラクト
└── tasks.md             # フェーズ 2: ドキュメント修正・実装タスク
```

### 成果物（リポジトリルート）

```text
README.md                # メイン・デプロイメント・ドキュメント（修正）
├── 新規: ghcr.io イメージ・ワンコマンド・クイックスタート・セクション
│   ├── git clone して docker compose up の手順
│   ├── docker pull コマンド
│   └── バージョン・ピン指定ガイド（本番環境向け）
├── 更新: Docker デプロイメント・ガイド
│   ├── ghcr.io イメージを主流として
│   └── ローカル・ビルド（docker build）を代替として
└── 更新: トラブルシューティング
    └── イメージ・プル失敗、認証等を追加

docker-compose.yml      # 既存ファイル（ghcr.io イメージ参照に更新）
.env.example            # 既存ファイル（必要に応じて更新）
```

**構造決定**: README の「クイックスタート」セクションを ghcr.io イメージを中心に再編成。`git clone → .env 設定 → docker compose up` をデフォルト推奨方法として明確化。Release assets への docker-compose.yml 含含は実装しない（複雑性回避）。

## フェーズ 0: 研究

### 解決すべき主要質問

1. **docker-compose.yml 利用パターン検証**
   - 研究: git リポジトリに docker-compose.yml を保管・管理する方法
   - 研究: ユーザーが git clone してそのまま使用可能な構成
   - 決定: git repo の docker-compose.yml を single source of truth として利用

2. **デプロイメント・ドキュメント構造**
   - 研究:初心者向けに明確な git clone → docker compose up フロー
   - 研究: README での手順説明ベストプラクティス
   - 決定: README に git clone → .env 設定 → docker compose up を段階的に記載

3. **バージョン・ピン指定・戦略**
   - 研究: docker-compose.yml でバージョン・ピン指定（v1.0.0）のベストプラクティス
   - 研究: .env.example で環境変数デフォルト値の定義方法
   - 決定: docker-compose.yml で image: ghcr.io/.../power-on-rpi:v1.0.0 のように具体的タグを指定

## フェーズ 1: 設計・コントラクト

### デプロイメント・モデル（data-model.md）

**エンティティ**:
- **DeploymentMethod**: デプロイ方法（GitClone、LocalBuild）
- **DockerComposeFile**: docker-compose.yml ファイル（repo 保管）
- **ImageSource**: イメージ・ソース（ghcr.io URL）
- **VersionTag**: バージョン指定（v1.0.0、latest）
- **EnvironmentVariable**: 環境変数（.env ファイル）

**関係**:
- DeploymentMethod references DockerComposeFile
- DockerComposeFile contains ImageSource
- ImageSource specifies VersionTag
- EnvironmentVariable referenced by docker-compose.yml

### docker-compose.yml ファイル・コントラクト（contracts/）

**コントラクト**: docker-compose.yml ファイル形式・必須フィールド
- version: "3.8"
- services: rpi-wol, pc-power
  - image: ghcr.io/shiomi680/power-on-rpi:v1.0.0（ローカル build オーバーライド可能）
  - ports: ["5000:5000"]、["5001:5001"]
  - environment: PC_ADDRESS、WOL_TARGET_MAC 等

### クイックスタート・シナリオ（quickstart.md）

1. **推奨パス: Git Clone + docker compose up**
   - git clone https://github.com/shiomi680/power-on
   - cd power-on
   - cp .env.example .env（編集）
   - docker compose up -d

2. **本番パス**: バージョン・ピン指定
   - docker-compose.yml で image: ghcr.io/shiomi680/power-on-rpi:v1.0.0 指定
   - docker compose up -d

3. **開発パス**: ローカル・ビルド
   - docker build -t power-on-rpi:dev ./rpi-wol
   - docker-compose.local.yml で build: override
   - docker compose -f docker-compose.local.yml up -d
