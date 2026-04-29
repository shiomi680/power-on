# 実装計画: ghcr.io プリビルト・イメージ・ワンコマンド・デプロイメント

**ブランチ**: `004-ghcr-quick-deploy` | **日付**: 2026-04-29 | **仕様**: [specs/004-ghcr-quick-deploy/spec.md](spec.md)
**入力**: `/specs/004-ghcr-quick-deploy/spec.md` の機能仕様

## 概要

既存の README デプロイメント・ドキュメントを改善し、ghcr.io からのプリビルト・イメージ取得をデフォルト・デプロイメント方法として最初に紹介する。docker pull → docker compose up ワンコマンド・デプロイを推奨し、ローカル・ビルドを代替オプションとして提供する。これにより、初心者ユーザーのデプロイ・ハードルが大幅に低下し、本番環境ではバージョン・ピン指定で再現性が確保される。

## 技術コンテキスト

**言語/形式**: Markdown ドキュメント修正  
**主要依存関係**: ghcr.io Docker Registry（既存）、docker-compose（既存）  
**ストレージ**: N/A  
**テスト**: コマンド実行検証（docker pull、docker compose up）  
**対象プラットフォーム**: GitHub README（公開ドキュメント）  
**プロジェクトタイプ**: ドキュメント更新  
**パフォーマンス目標**: 2 分以内にシステム起動（SC-002）  
**制約**: 初心者向け明確性、完全なコマンド例、バージョン管理  
**スコープ**: README.md クイックスタート・セクション修正・拡張

## 憲法チェック

*ゲート: フェーズ 0 研究前に合格必須。フェーズ 1 設計後に再確認。*

| 原則 | 状態 | 備考 |
|------|------|------|
| I. 日本語優先 | ✅ 合格 | ドキュメント・計画・コミットメッセージが日本語。技術用語（ghcr、Docker、WOL 等）は原語。 |
| II. ライブラリファースト | ⚠️ 非該当 | 既存ドキュメント更新、新規ライブラリ作成ではない。 |
| III. CLI インターフェース | ⚠️ 非該当 | ドキュメント作業であり、CLI インターフェース作成ではない。 |
| IV. テスト優先 | ✅ 合格 | SC-001～SC-005 で測定可能なテスト基準を定義。docker pull・docker compose up が実行可能で検証。 |
| V. 統合テスト重視 | ✅ 合格 | docker pull + docker compose up のエンドツーエンド・デプロイメント検証。 |

**結果**: 合格 - ドキュメント更新作業で憲法違反なし。フェーズ 0 に進行。

## プロジェクト構造

### ドキュメント（本機能）

```text
specs/004-ghcr-quick-deploy/
├── plan.md              # このファイル
├── research.md          # フェーズ 0: ghcr イメージ・スキーム、docker-compose ベストプラクティス
├── data-model.md        # フェーズ 1: デプロイメント・モデル（ghcr vs ローカル・ビルド）
├── quickstart.md        # フェーズ 1: ワンコマンド・デプロイメント・シナリオ
├── contracts/           # フェーズ 1: docker-compose ファイル・コントラクト
└── tasks.md             # フェーズ 2: ドキュメント修正・追加タスク（/speckit-tasks で作成）
```

### 成果物（リポジトリルート）

```text
README.md                # メイン・デプロイメント・ドキュメント（修正）
├── 更新: クイックスタート・セクション
│   └── ghcr.io イメージ・ワンコマンド（推奨）をトップに配置
├── 新規: ghcr.io イメージ・プル・セクション
│   ├── docker pull コマンド
│   ├── 利用可能なバージョン・タグ
│   └── docker-compose.yml での参照方法
├── 更新: Docker デプロイメント・ガイド
│   ├── ghcr.io イメージを主流として
│   └── ローカル・ビルド（docker build）を代替として
├── 新規: バージョン・ピン指定ガイド
│   └── 本番デプロイメント向けの再現性
└── 更新: トラブルシューティング
    └── イメージ・プル失敗、認証、レジストリ・エラー等を追加
```

**構造決定**: README の「クイックスタート」セクションを ghcr.io イメージを中心に再編成。docker pull + docker compose up をデフォルト推奨方法とし、ローカル・ビルドは「開発・カスタマイズ向け」として説明。

## フェーズ 0: 研究

### 解決すべき主要質問

1. **ghcr.io イメージ・スキーム検証**
   - 研究: 既存のイメージ・タグ・スキーム（semver、latest、sha など）を確認
   - 研究: GitHub Container Registry のアクセス制限（認証必須か否か）
   - 決定: パブリック・イメージと仮定、semver タグ（v1.0.0）をピン指定推奨

2. **docker-compose.yml イメージ参照方法**
   - 研究: docker-compose で ghcr.io イメージを参照するベストプラクティス
   - 研究: ローカル・ビルド・オーバーライド・パターン（image vs build キー）
   - 決定: デフォルト image: ghcr.io/..., ローカルは build: ./rpi-wol でオーバーライド

3. **イメージ取得失敗時の対処**
   - 研究: docker pull が失敗する一般的なシナリオ（レジストリ・ダウン、認証、プロキシ）
   - 研究: オフライン環境でのフォールバック方法（ローカル・ビルド）
   - 決定: トラブルシューティング・セクションでレジストリ認証・プロキシ設定を説明

4. **バージョン・ピン指定・戦略**
   - 研究: 本番向けのバージョン・ピン指定ベストプラクティス
   - 研究: セマンティック・バージョニング適用方法
   - 決定: `v1.0.0` のように具体的タグを推奨、`latest` は開発・テスト用のみ

## フェーズ 1: 設計・コントラクト

### デプロイメント・モデル（data-model.md）

**エンティティ**:
- **DeploymentMethod**: デプロイ方法（GHCR、LocalBuild）
- **ImageSource**: イメージ・ソース（ghcr.io URL、ローカル・ビルド）
- **VersionTag**: バージョン指定（latest、v1.0.0、sha256:...）
- **DockerCompose**: デプロイ・設定（イメージ、ポート、環境変数）

**関係**:
- DeploymentMethod has ImageSource
- ImageSource specifies VersionTag
- DockerCompose references ImageSource

### docker-compose ファイル・コントラクト（contracts/）

**コントラクト**: docker-compose.yml ファイル形式・必須フィールド
- version: "3.8"
- services: rpi-wol, pc-power
  - image: ghcr.io/shiomi680/power-on-rpi:v1.0.0（またはローカル build パス）
  - ports: ["5000:5000"]、["5001:5001"]
  - environment: PC_ADDRESS、WOL_TARGET_MAC 等

### クイックスタート・シナリオ

1. **最速パス（5 分）**: ghcr.io イメージ・ワンコマンド
   - docker pull ghcr.io/shiomi680/power-on-rpi:latest
   - docker compose up -d
   - curl http://localhost:5000/health

2. **本番パス（5 分）**: バージョン・ピン指定
   - docker-compose.yml で image: ghcr.io/shiomi680/power-on-rpi:v1.0.0 指定
   - docker compose up -d
   - 検証

3. **開発パス（10 分）**: ローカル・ビルド
   - docker build -t power-on-rpi:dev ./rpi-wol
   - docker compose -f docker-compose.local.yml up -d
   - 検証

## 複雑性追跡

憲法違反なし確認済み。これはドキュメント更新作業で、既存仕様（003-deployment-readme）の改善です。
