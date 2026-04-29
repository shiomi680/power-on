# タスク一覧: ghcr.io プリビルト・イメージ・ワンコマンド・デプロイメント

**フィーチャー**: 004-ghcr-quick-deploy  
**作成日**: 2026-04-30  
**仕様**: [spec.md](spec.md) | **計画**: [plan.md](plan.md)

**入力**: `/specs/004-ghcr-quick-deploy/spec.md` の 3 つのユーザーストーリー (US1 P1, US2 P1, US3 P2)

**組織**: タスクはユーザーストーリー別に整理。各ストーリーを独立して実装・テスト・納品可能に。

## フォーマット: `- [ ] [ID] [P?] [Story?] 説明: ファイルパス`

- **[P]**: 並行実行可能（異なるファイル・依存なし）
- **[Story]**: ユーザーストーリー（US1, US2, US3）
- 説明には正確なファイルパス・コマンドを含める

---

## フェーズ 1: セットアップ（共有インフラ）

**目的**: プロジェクト初期化・基本構造確認

- [x] T001 プロジェクト構造確認: .env.example、docker-compose.yml、version.json、.github/workflows/ が存在
- [x] T002 既存 README.md を確認: 現在のクイックスタート・セクション・デプロイメント手順をレビュー

---

## フェーズ 2: ユーザーストーリー 1 - ワンコマンド・デプロイ (P1) 🎯 MVP

**目標**: 初心者ユーザーが `docker compose up` でシステムを 2 分以内に起動可能に

**独立テスト基準**:
- docker-compose.yml で ghcr.io イメージ（v1.0.0）を参照
- README にクイックスタート・セクション（git clone → .env → docker compose up）が明記
- docker compose up でシステムが起動し、ヘルスチェック・エンドポイントに正常応答

### ユーザーストーリー 1 - 実装

- [x] T003 [US1] README.md 更新: **クイックスタート（5分）** セクションを追加 - git clone → .env.example コピー → .env 編集 → docker compose up フロー
- [x] T004 [US1] README.md 更新: docker-compose.yml での ghcr.io イメージ参照例・docker pull コマンド説明を追加
- [x] T005 [US1] docker-compose.yml 確認: raspi-wol サービスが `ghcr.io/shiomi680/power-on-rpi:v1.0.0` を参照していることを確認
- [x] T006 [US1] docker-compose.yml 確認: pc-power サービスが `ghcr.io/shiomi680/power-on-pc:v1.0.0` を参照していることを確認
- [x] T007 [US1] README.md 追加: ヘルスチェック・エンドポイント確認コマンド - `curl http://localhost:5000/api/health`、`curl http://localhost:5001/api/health`
- [x] T008 [US1] テスト実行: docker compose up → 両サービス起動確認 → ヘルスチェック確認（US1 受け入れシナリオ検証）

---

## フェーズ 3: ユーザーストーリー 2 - バージョン・ピン (P1)

**目標**: 本番運用ユーザーが検証済みイメージバージョンをピン指定してデプロイ可能に

**独立テスト基準**:
- docker-compose.yml で明確なバージョン・タグ（v1.0.0）が指定
- README に「本番環境でのバージョン・ピン指定」セクションが記載
- タグを切り替えて docker compose up で異なるバージョンが起動可能

### ユーザーストーリー 2 - 実装

- [x] T009 [US2] docker-compose.yml 確認: イメージ・タグが明確に v1.0.0 指定（または .env から動的参照確認）
- [x] T010 [US2] README.md 追加: **本番環境でのバージョン・ピン指定** セクション - バージョン・タグ切り替え方法（docker-compose.yml 直接編集またはシェル変数例）
- [x] T011 [US2] README.md 追加: version.json 役割説明・バージョン確認方法 (`cat version.json`)
- [x] T012 [US2] テスト実行: docker-compose.yml タグを v1.0.0 → v1.1.0（架空）に変更して docker compose up が新バージョンを引く動作確認

---

## フェーズ 4: ユーザーストーリー 3 - ローカル・ビルド代替路 (P2)

**目標**: 開発者がカスタマイズ後、ローカル・ビルド・オプションで独自イメージを構築・デプロイ可能に

**独立テスト基準**:
- docker-compose.local.yml が作成され、`build:` オプションで Dockerfile を参照
- README に「ローカル・ビルド・カスタマイズ」セクションが記載
- docker compose -f docker-compose.local.yml up でローカル・イメージから起動可能

### ユーザーストーリー 3 - 実装

- [x] T013 [P] [US3] docker-compose.local.yml を作成（ルート）: rpi-wol・pc-power の `build: { context: ./rpi-wol, dockerfile: Dockerfile }`・`build: { context: ./pc-power, dockerfile: Dockerfile }` オプション指定
- [x] T014 [P] [US3] rpi-wol/docker-compose.local.yml を作成: raspi 単体ローカル・ビルド・パターン - `image: power-on-rpi:local`、`build: { context: ., dockerfile: Dockerfile }`
- [x] T015 [P] [US3] pc-power/docker-compose.local.yml を作成: pc 単体ローカル・ビルド・パターン - `image: power-on-pc:local`、`build: { context: ., dockerfile: Dockerfile }`
- [x] T016 [US3] README.md 追加: **開発・カスタマイズ（ローカル・ビルド）** セクション - docker-compose.local.yml 使用方法・`docker compose -f docker-compose.local.yml up -d` コマンド例
- [x] T017 [US3] README.md 追加: Dockerfile 修正例・docker build コマンド（`docker build -t power-on-rpi:local ./rpi-wol`）・docker compose.local.yml で起動方法
- [x] T018 [US3] テスト実行: docker-compose.local.yml で docker compose up が実行可能であることを確認（US3 受け入れシナリオ検証）

---

## フェーズ 5: ポーランド - アーキテクチャ・セクション分離

**目的**: README を整理し、想定構成・プラットフォーム別インストール・セクションを分離

### ポーランド・タスク

- [x] T019 README.md 更新: **想定構成・アーキテクチャ** セクションを追加
  - システム・コンポーネント説明: raspi-wol（WOL マジックパケット送信）、pc-power（電源制御 API）、PC（対象マシン）
  - 通信フロー: Raspberry Pi → PC_ADDRESS（ネットワーク経由）→ PC（WOL/シャットダウン）
  - ネットワーク構成例: `192.168.1.x` 範囲での Raspberry Pi・PC 配置

- [x] T020 [P] rpi-wol/docker-compose.yml を作成（新規）: raspi 独立構成
  - イメージ: `ghcr.io/shiomi680/power-on-rpi:v1.0.0`
  - ポート: 5000
  - 環境変数: `PC_ADDRESS`、`WOL_TARGET_MAC`、`WOL_BROADCAST_IP`

- [x] T021 [P] pc-power/docker-compose.yml を作成（新規）: pc 独立構成
  - イメージ: `ghcr.io/shiomi680/power-on-pc:v1.0.0`
  - ポート: 5001
  - 環境変数: `SHUTDOWN_TIMEOUT`

- [x] T022 README.md セクション再構成・統合:
  - 目次更新
  - **クイックスタート（5分）** - 両サービス統合デプロイ
  - **想定構成・アーキテクチャ** - システム概要（T019 で作成）
  - **Raspberry Pi インストール** - PC_ADDRESS、WOL_TARGET_MAC 設定・raspi 単体デプロイ（rpi-wol/docker-compose.yml）
  - **PC インストール** - pc 単体デプロイ方法（pc-power/docker-compose.yml）
  - **ローカル・ビルド・カスタマイズ** - docker-compose.local.yml 使用方法（T016 で作成）
  - **トラブルシューティング** - 既存セクション保持
  - **参考資料** - DOCKER.md、CI-CD.md リンク

- [x] T023 README.md 最終確認: すべてのコマンド例・ファイルパス・構成が正確・完全であることを検証

---

## 依存関係・実行順序

```
フェーズ 1: セットアップ (T001-T002)
    ↓
フェーズ 2: US1 - ワンコマンド・デプロイ (T003-T008)
    ↓ 依存
フェーズ 3: US2 - バージョン・ピン (T009-T012) [並行可]
    ↓
フェーズ 4: US3 - ローカル・ビルド (T013-T018) [T013-T015 並行可]
    ↓
フェーズ 5: ポーランド - アーキテクチャ・セクション分離 (T019-T023) [T020-T021 並行可]
```

## タスク統計

- **総タスク数**: 23
- **セットアップ・タスク**: 2 (T001-T002)
- **US1 タスク**: 6 (T003-T008)
- **US2 タスク**: 4 (T009-T012)
- **US3 タスク**: 6 (T013-T018)
- **ポーランド・タスク**: 5 (T019-T023)

## 並行実行機会

- **T013-T015**: docker-compose.local.yml ファイル作成（異なるファイル・依存なし）
- **T020-T021**: コンポーネント別 docker-compose.yml 作成（異なるディレクトリ・依存なし）

## 推奨 MVP スコープ

**MVP**: US1 + US2 + アーキテクチャ概要
- フェーズ 1-3: T001-T012
- フェーズ 5: T019、T022-T023

**完全版**: すべてのユーザーストーリー + ローカル・ビルド
- フェーズ 1-5: T001-T023
- US3（ローカル・ビルド）はマイナー機能で P2 優先度

## フォーマット検証

✅ **すべてのタスクは以下フォーマットに従う**:
- `- [ ]` チェックボックス（未完了）
- `T###` タスク ID
- `[P]` 並行可能な場合のみ表示
- `[Story]` ユーザーストーリー・ラベル（US1、US2、US3）
- ファイルパス付き説明（正確なディレクトリ・ファイル名）

**サンプル準拠例**:
- ✅ `- [ ] T003 [US1] README.md 更新: クイックスタート・セクションを追加`
- ✅ `- [ ] T013 [P] [US3] docker-compose.local.yml を作成: build オプション指定`
- ✅ `- [ ] T020 [P] rpi-wol/docker-compose.yml を作成: ghcr.io イメージ参照`
