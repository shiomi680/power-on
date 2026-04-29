# 実装計画: ghcr.io プリビルト・イメージ・ワンコマンド・デプロイメント

**ブランチ**: `004-ghcr-quick-deploy` | **作成日**: 2026-04-30 | **仕様書**: [spec.md](spec.md)
**入力**: `/specs/004-ghcr-quick-deploy/spec.md`

**注記**: このドキュメントは `/speckit-plan` コマンドで記入されます。

## サマリー

ユーザーが `git clone` → `docker compose up` でシステムを即座に起動可能にするため、以下を実装します：

- **ghcr.io プリビルト・イメージ・デフォルト**: docker-compose.yml で ghcr.io イメージをデフォルト参照
- **pc-power・raspi の独立構成**: 各コンポーネント（pc-power/、rpi-wol/）に docker-compose.yml を配置し、ghcr.io イメージを指定
- **ローカル・ビルド代替路**: docker-compose.local.yml でローカル・ビルド・パターンを提供（開発者向け）
- **プラットフォーム別 README セクション**: Raspberry Pi インストール・セクション、PC インストール・セクション、想定構成・アーキテクチャを明確に分離
- **ワンコマンド・デプロイメント**: `.env.example` から `.env` を編集して `docker compose up` で起動

## 技術コンテキスト

**形式/プラットフォーム**: ドキュメント + Docker Compose 設定ファイル  
**主要依存関係**: Docker（v20.10+）、Docker Compose（v2.0+）、ghcr.io（プリビルト・イメージ）  
**ストレージ**: なし（設定ファイル・ドキュメント のみ）  
**テスト**: 実行テスト（docker compose up 検証、ヘルスチェック・エンドポイント確認）  
**対象プラットフォーム**: Raspberry Pi（Linux）、PC（Linux/Windows/macOS）  
**プロジェクトタイプ**: マルチ・コンポーネント・デプロイメント・ガイド + Docker 設定  
**制約**: 
- ユーザーは Docker インストール環境を前提
- ghcr.io レジストリへのアクセス必須（パブリック・イメージ）
- ローカル・ビルド・パターンは開発者向け（ビルド・ツール必須）

## 憲法チェック

*ゲート: フェーズ 0 研究前に合格必須。フェーズ 1 設計後に再確認。*

| 原則 | 状態 | 備考 |
|------|------|------|
| I. 日本語優先 | ✅ 合格 | README セクション・ドキュメントは日本語で記述。技術用語（Docker、ghcr.io など）は原語のまま使用。 |
| II. ライブラリファースト | ⚠️ 非該当 | 本機能はドキュメント・設定ファイル作業で、新規ライブラリ実装ではない。既存ライブラリの設定・紹介 |
| III. CLI インターフェース | ⚠️ 非該当 | Docker Compose コマンド（docker compose up など）を使用。新規 CLI 開発ではない。 |
| IV. テスト優先 | ✅ 合格 | スペックに受け入れシナリオ・テスト基準を明記。ドキュメント実装後に docker compose up で動作確認テスト。 |
| V. 統合テスト重視 | ✅ 合格 | マルチ・コンポーネント（raspi WOL + PC API）統合デプロイメント・シナリオをテスト。 |

**結果**: 合格 - ドキュメント・設定ファイル作業で憲法違反なし。フェーズ 0 に進行。

## プロジェクト構造

### ドキュメント（本機能）

```text
specs/004-ghcr-quick-deploy/
├── plan.md                        # このファイル
├── spec.md                        # 仕様書（既存）
├── tasks.md                       # フェーズ 2 で作成（/speckit-tasks コマンド）
├── research.md                    # フェーズ 0: デプロイメント・ベストプラクティス
├── data-model.md                  # フェーズ 1: 構成・スキーマ定義
├── contracts/                     # フェーズ 1: docker-compose.yml スキーマ
└── quickstart.md                  # フェーズ 1: デプロイメント例シナリオ
```

### 成果物（リポジトリルート）

```text
.
├── README.md                      # 更新：プラットフォーム別インストール・セクション分離
├── .env.example                   # 既存：環境変数テンプレート
├── docker-compose.yml             # 更新：ghcr.io イメージ + raspi デフォルト指定
├── docker-compose.local.yml       # 新規：ローカル・ビルド・パターン（開発者向け）
├── version.json                   # 既存：バージョン管理
├── rpi-wol/
│   ├── docker-compose.yml         # 新規：raspi 独立構成（ghcr.io イメージ）
│   ├── docker-compose.local.yml   # 新規：raspi ローカル・ビルド・パターン
│   └── ... (既存ファイル)
├── pc-power/
│   ├── docker-compose.yml         # 新規：pc 独立構成（ghcr.io イメージ）
│   ├── docker-compose.local.yml   # 新規：pc ローカル・ビルド・パターン
│   └── ... (既存ファイル)
└── .github/
    └── workflows/
        └── docker-publish.yml     # 既存：CI/CD（ghcr.io 自動プッシュ）
```

**構造の決定**:
- **ghcr.io デフォルト**: docker-compose.yml はプリビルト・イメージ（ghcr.io）をデフォルト参照
- **コンポーネント独立構成**: pc-power/ と rpi-wol/ に各々 docker-compose.yml を配置（他のコンポーネント不要なデプロイに対応）
- **ローカル・ビルド代替**: docker-compose.local.yml でローカル・ビルド・パターンを提供（開発者・カスタマイズ用）
- **README 分離**: raspi インストール・セクション、pc インストール・セクション、想定構成・アーキテクチャを明確に分離

## フェーズ 0: 研究

### 解決すべき主要質問

1. **Docker Compose マルチプロジェクト・パターン**
   - 決定: 各コンポーネント（pc-power/、rpi-wol/）に独立した docker-compose.yml を配置
   - 理由: コンポーネント単体デプロイを可能にするため（raspi のみ、または pc のみ を構築可能）

2. **ghcr.io イメージ・バージョン指定**
   - 決定: docker-compose.yml で明確なバージョン・タグを指定（例：`v1.0.0`）
   - 理由: 本番環境の再現性・安定性確保

3. **ローカル・ビルド・パターン**
   - 決定: docker-compose.local.yml で `build:` オプションを使用（ローカル Dockerfile を参照）
   - 理由: 開発者が修正・カスタマイズ後、ローカル・イメージで検証可能に

4. **README セクション分離**
   - 決定: クイックスタート（両コンポーネント）、raspi インストール、pc インストール、想定構成を明確に分離
   - 理由: ユーザーが自分の環境に合わせたセクションを選択可能に

## フェーズ 1: 設計

### docker-compose.yml 構成モデル

**ルート docker-compose.yml**（両サービス統合）
- raspi-wol サービス: ghcr.io イメージ（v1.0.0）
- pc-power サービス: ghcr.io イメージ（v1.0.0）
- Network: power-on-network
- Health checks: 各サービスの /api/health エンドポイント

**pc-power/docker-compose.yml**（PC 単体）
- pc-power サービス: ghcr.io イメージ（v1.0.0）
- ポート: 5001
- 環境変数: FLASK_HOST、FLASK_PORT、SHUTDOWN_TIMEOUT

**rpi-wol/docker-compose.yml**（Raspberry Pi 単体）
- rpi-wol サービス: ghcr.io イメージ（v1.0.0）
- ポート: 5000
- 環境変数: FLASK_HOST、FLASK_PORT、PC_ADDRESS、WOL_TARGET_MAC、WOL_BROADCAST_IP

**docker-compose.local.yml**（ローカル・ビルド代替）
- `build: { context: ./<component>, dockerfile: Dockerfile }` でローカル・イメージ構築
- イメージ・タグ: power-on-rpi:local、power-on-pc:local（衝突回避）

### README コンテンツ・スキーマ

**セクション構成**:
1. クイックスタート（5分）: ワンコマンド・デプロイ（両サービス）
2. 想定構成・アーキテクチャ: システムコンポーネント・通信フロー図
3. Raspberry Pi インストール: PC_ADDRESS、WOL_TARGET_MAC 設定、raspi 独立デプロイ
4. PC インストール: PC 単体デプロイ方法
5. ローカル・ビルド・カスタマイズ: docker-compose.local.yml 使用方法
6. トラブルシューティング: 既存セクション
7. 参考資料: DOCKER.md、CI-CD.md リンク

### クイックスタート・シナリオ

1. **開発者向けワンコマンド**
   ```bash
   git clone https://github.com/shiomi680/power-on
   cd power-on
   cp .env.example .env
   docker compose up -d
   curl http://localhost:5000/api/health  # raspi-wol 確認
   curl http://localhost:5001/api/health  # pc-power 確認
   ```

2. **Raspberry Pi 単体デプロイ**
   ```bash
   cd rpi-wol
   cp ../.env.example .env
   # (PC_ADDRESS、WOL_TARGET_MAC を編集)
   docker compose up -d
   ```

3. **PC 単体デプロイ**
   ```bash
   cd pc-power
   docker compose up -d
   ```

4. **ローカル・ビルド・カスタマイズ**
   ```bash
   # イメージを編集
   docker compose -f docker-compose.local.yml up -d
   ```

## 複雑性追跡

憲法チェック合格。ドキュメント・設定ファイル作業のため、複雑性なし。
