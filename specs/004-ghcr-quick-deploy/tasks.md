# 実装タスク: ghcr.io プリビルト・イメージ・ワンコマンド・デプロイメント

**機能**: ghcr.io プリビルト・イメージ・ワンコマンド・デプロイメント  
**ブランチ**: `004-ghcr-quick-deploy`  
**総タスク数**: 20  
**実装戦略**: MVP スコープ（US1 + US2 = 初心者 + 本番デプロイ）、その後 US3（ローカル・ビルド）を追加。各USでテスト仕様定義 → 実装 → テスト実行（Red-Green-Refactor）

---

## 依存関係・実行順序

### ストーリー依存関係

```
フェーズ 2（基盤） ─→ フェーズ 3（US1）─┐
                      フェーズ 4（US2）├→ フェーズ 5（US3）→ フェーズ 6（Polish）
```

### 並列実行

- **フェーズ 2**: T002-T005 並列化可能 [P]
- **フェーズ 3（US1）**: T006（テスト仕様） → T007-T009（実装、並列化可能 [P]） → T010（テスト実行）
- **フェーズ 4（US2）**: T011（テスト仕様） → T012-T013（実装、並列化可能 [P]） → T014（テスト実行）
- **フェーズ 5（US3）**: T015（テスト仕様） → T016-T017（実装、並列化可能 [P]） → T018（テスト実行）

---

## フェーズ 1: セットアップ

### 目標
ドキュメント・修正・追加の準備。

### 独立テスト基準
- 既存の README.md が保持・バージョン管理中
- docker-compose.yml が存在・更新可能な状態
- .env.example が存在

### タスク

- [ ] T001 既存の README.md、docker-compose.yml、.env.example が無傷か確認・バックアップを取得

---

## フェーズ 2: 基盤（ブロッキング前提条件）

### 目標
README 基本構造と docker-compose.yml を ghcr.io イメージ参照に更新。

### 独立テスト基準
- README に「クイックスタート」セクション・スタブが存在
- docker-compose.yml が ghcr.io イメージを参照（image: ghcr.io/...）
- .env.example に全環境変数が列挙

### タスク

- [ ] T002 [P] README.md の先頭に「クイックスタート」セクションのスタブを作成 (README.md クイックスタート・セクション)
- [ ] T003 [P] docker-compose.yml で rpi-wol の ghcr.io イメージを参照するように更新（image: ghcr.io/shiomi680/power-on-rpi:v1.0.0） (docker-compose.yml services.rpi-wol)
- [ ] T004 [P] docker-compose.yml で pc-power の ghcr.io イメージを参照するように更新（image: ghcr.io/shiomi680/power-on-pc:v1.0.0） (docker-compose.yml services.pc-power)
- [ ] T005 [P] .env.example に PC_ADDRESS、WOL_TARGET_MAC、WOL_BROADCAST_IP、FLASK_PORT、LOG_LEVEL、SHUTDOWN_TIMEOUT を記載 (.env.example)

---

## フェーズ 3: ユーザーストーリー 1 - git clone → docker compose up [P1]

### ストーリー目標
初心者ユーザーが git clone → .env 設定 → docker compose up の 3 ステップでシステムを起動できるようにする。

### 受け入れ基準（仕様書より）
1. README のクイックスタート・セクションに git clone 手順が記載
2. 初心者ユーザーが README の手順に従って 5-10 分以内にシステムを起動可能（SC-002: 2 分以内）
3. ヘルスチェック・エンドポイントが正常に応答

### 独立テスト基準
- README クイックスタート・セクションが git clone → .env 設定 → docker compose up を説明
- すべてのコマンドがコピペ可能・テスト済み
- 期待される出力・成功インジケータが明示

### タスク

- [ ] T006 [US1] テスト仕様定義：quickstart.md「シナリオ 1: Git Clone」の検証手順を README テストテンプレートに記載 (README.md クイックスタート・セクション)
  - git clone 実行時の期待される出力（"Cloning into 'power-on'"）
  - ls -la で README.md、docker-compose.yml、rpi-wol/、pc-power/ が存在
  - .env ファイルコピー・編集方法
  - docker compose up -d 実行後の期待される状態
  - curl http://localhost:5000/api/health と curl http://localhost:5001/api/health が 200 OK を返す

- [ ] T007 [P] [US1] README「クイックスタート」セクションに git clone https://github.com/shiomi680/power-on && cd power-on の手順を記載 (README.md クイックスタート・セクション)

- [ ] T008 [P] [US1] README「クイックスタート」セクションに cp .env.example .env と環境変数編集（PC_ADDRESS、WOL_TARGET_MAC）をドキュメント化 (README.md クイックスタート・セクション)

- [ ] T009 [P] [US1] README「クイックスタート」セクションに docker compose up -d と 2 分以内の起動確認、ヘルスチェック（curl http://localhost:5000/api/health、curl http://localhost:5001/api/health）をドキュメント化 (README.md クイックスタート・セクション)

- [ ] T010 [US1] テスト実行・検証：T006 で定義した検証手順に基づいて、README「クイックスタート」セクションのコマンドを実際に実行し、すべての期待される結果が得られることを確認 (README.md クイックスタート・セクション)

---

## フェーズ 4: ユーザーストーリー 2 - バージョン・ピン指定（本番向け） [P1]

### ストーリー目標
本番運用ユーザーが特定の検証済みイメージバージョン（v1.0.0 等）をピン指定してデプロイし、再現性を確保できるようにする。

### 受け入れ基準（仕様書より）
1. README に特定バージョン・タグ（v1.0.0）のピン指定方法が説明
2. docker-compose.yml で具体的なバージョン・タグが指定可能
3. バージョン・タグの切り替え（v1.0.0 → v1.1.0）が可能で動作確認

### 独立テスト基準
- README に「本番デプロイメント向けバージョン・ピン指定」セクションが存在
- docker-compose.yml で image: ghcr.io/shiomi680/power-on-rpi:v1.0.0 ように具体的バージョンが指定
- 複数バージョン・タグでの切り替え方法が明確

### タスク

- [ ] T011 [US2] テスト仕様定義：quickstart.md「シナリオ 2: バージョン・ピン指定」の検証手順を README テストテンプレートに記載 (README.md 本番環境セクション)
  - docker-compose.yml で image: ghcr.io/shiomi680/power-on-rpi:v1.0.0 が指定されていることを確認（grep image:）
  - 複数バージョン（v1.0.0、v1.1.0）への切り替え方法が明確
  - バージョン切り替え後、docker compose up -d で正しいバージョンが起動される

- [ ] T012 [P] [US2] README に「本番環境でのバージョン・ピン指定」セクションを追加し、docker-compose.yml での image: ghcr.io/shiomi680/power-on-rpi:v1.0.0 指定方法を説明 (README.md 本番環境セクション)

- [ ] T013 [P] [US2] README に異なるバージョン・タグ（v1.0.0、v1.1.0 等）への切り替え方法を記載し、再現性確保の重要性を説明 (README.md 本番環境セクション)

- [ ] T014 [US2] テスト実行・検証：T011 で定義した検証手順に基づいて、docker-compose.yml のバージョン指定が正しいこと、複数バージョン切り替えが可能であることを確認 (README.md 本番環境セクション)

---

## フェーズ 5: ユーザーストーリー 3 - ローカル・ビルド代替路 [P2]

### ストーリー目標
開発者がコード修正後、ローカル・ビルド・オプションで独自イメージを作成・テストできるようにする。

### 受け入れ基準（仕様書より）
1. README に docker build ワークフローが説明
2. ローカル・ビルド・イメージで docker-compose を使用して起動可能
3. build: オーバーライドまたは docker-compose.local.yml パターンが示されている

### 独立テスト基準
- README に「開発・カスタマイズ（ローカル・ビルド）」セクションが存在
- docker build コマンドがコピペ可能・テスト済み
- ローカル・ビルド・イメージでの docker-compose 参照方法が明確

### タスク

- [ ] T015 [US3] テスト仕様定義：quickstart.md「シナリオ 3: ローカル・ビルド」の検証手順を README テストテンプレートに記載 (README.md 開発・カスタマイズセクション)
  - docker build -t power-on-rpi:dev ./rpi-wol 実行時の期待される出力
  - docker build -t power-on-pc:dev ./pc-power 実行時の期待される出力
  - docker-compose.local.yml での build: override パターン
  - docker compose -f docker-compose.local.yml up -d でローカル・イメージが起動される

- [ ] T016 [P] [US3] README に「開発・カスタマイズ（ローカル・ビルド）」セクションを追加し、docker build -t power-on-rpi:dev ./rpi-wol と docker build -t power-on-pc:dev ./pc-power コマンドを記載 (README.md 開発・カスタマイズセクション)

- [ ] T017 [P] [US3] README に docker-compose.local.yml で build: ./rpi-wol、build: ./pc-power をオーバーライドするパターン、またはローカル・イメージでの起動方法（docker compose -f docker-compose.local.yml up -d）を記載 (README.md 開発・カスタマイズセクション)

- [ ] T018 [US3] テスト実行・検証：T015 で定義した検証手順に基づいて、docker build コマンドが成功し、docker-compose.local.yml でローカル・イメージが起動できることを確認 (README.md 開発・カスタマイズセクション)

---

## フェーズ 6: ポーランド・クロスカッティング

### 目標
仕上げ、検証、トラブルシューティング・セクション追加。

### タスク

- [ ] T019 README.md に「トラブルシューティング」セクションを追加し、以下を記載:
  - イメージ・プル失敗時の対処（docker pull ... が失敗）
  - ポート競合時の対処（port ... already in use）
  - ネットワーク接続エラー対処（PC_ADDRESS に到達不可）
  - ヘルスチェック失敗時の診断
  - レジストリ認証エラー対処（認証が必要な場合）
  (README.md トラブルシューティング・セクション)

- [ ] T020 README 全体の整合性・トーン・明確性を校正・確認し、すべてのコマンド例がテスト済みであることを検証 (README.md 全体)

---

## 実装戦略

### MVP スコープ（推奨・最初のイテレーション）
**タスク**: T001-T014（約 3-4 時間）
- ✅ フェーズ 1: セットアップ
- ✅ フェーズ 2: 基盤（README header + docker-compose.yml 更新）
- ✅ フェーズ 3: US1（テスト仕様定義 → 実装 → テスト実行）
- ✅ フェーズ 4: US2（テスト仕様定義 → 実装 → テスト実行）

**成果**: ghcr.io イメージを初心者向けワンコマンド・デプロイメントとして確立。本番環境はバージョン・ピン指定で再現性確保。Red-Green-Refactor サイクルで検証済み。

### フル・スコープ（2 番目のイテレーション）
**タスク**: T015-T020（約 2-3 時間）
- ✅ フェーズ 5: US3（テスト仕様定義 → 実装 → テスト実行）
- ✅ フェーズ 6: ポーランド・トラブルシューティング

**成果**: 完全なデプロイメント・ドキュメント（初心者 + 本番 + 開発・カスタマイズ）。すべての US で Red-Green-Refactor サイクル完備。

---

## サマリー

| 指標 | 値 |
|------|-----|
| 総タスク数 | 20 |
| MVP タスク（US1 + US2） | 14 |
| セットアップ・フェーズ | 1 タスク |
| 基盤フェーズ | 4 タスク |
| US1（git clone デプロイ） [P1] | 5 タスク（テスト仕様+実装 3+実行） |
| US2（バージョン・ピン指定） [P1] | 4 タスク（テスト仕様+実装 2+実行） |
| US3（ローカル・ビルド） [P2] | 4 タスク（テスト仕様+実装 2+実行） |
| ポーランド・フェーズ | 2 タスク |
| 並列化可能なタスク | 9（[P] でマーク：実装タスク群） |
| 推定時間（MVP） | 3～4 時間 |
| 推定時間（フル） | 5～6 時間 |

---

## 要件へのカバレッジ・マッピング

### 機能要件 → タスク

| 要件 | タスク | カバレッジ |
|------|--------|----------|
| FR-001: docker pull コマンドを明記 | T006（仕様定義）、T007-T009（実装）、T010（検証） | ✅ |
| FR-002: docker-compose.yml で ghcr.io イメージを参照 | T003-T004、T007-T009 | ✅ |
| FR-003: バージョン・ピン指定方法 | T011（仕様定義）、T012-T013（実装）、T014（検証） | ✅ |
| FR-004: ghcr.io がデフォルト推奨方法 | T006-T010、T012-T014 | ✅ |
| FR-005: ローカル・ビルド代替方法を記載 | T015（仕様定義）、T016-T017（実装）、T018（検証） | ✅ |
| FR-006: docker-compose.yml で ghcr.io デフォルト参照 | T003-T004 | ✅ |
| FR-007: イメージ取得失敗時のトラブルシューティング | T019 | ✅ |
| FR-008: git clone で入手可能な状態を確保 | T002、T006-T010 | ✅ |

### 成功基準 → 検証

| 成功基準 | 検証タスク | 期待される成果 |
|---------|-----------|-------------|
| SC-001: docker pull コマンド 1 行でイメージ取得可能 | T006-T010 | docker pull がコピペ可能・実装・テスト検証済み |
| SC-002: 2 分以内にシステム起動可能 | T009、T010 | docker compose up の実装・テスト検証済み（2分以内を実測確認） |
| SC-003: README だけでローカル・ビルド実行可能 | T015-T018 | docker build・docker-compose override パターン明確・テスト検証済み |
| SC-004: ghcr.io がデフォルト推奨方法として表示 | T006-T010、T012-T014 | README クイックスタート・本番セクションで確認・テスト検証済み |
| SC-005: ビルド・ツールなしにデプロイ可能 | T007-T010 | ghcr.io イメージ使用で build 不要・テスト検証済み |
