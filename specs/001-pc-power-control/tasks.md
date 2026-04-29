# タスク: リモートPC電源制御システム

**入力**: `/specs/001-pc-power-control/` の設計ドキュメント  
**前提条件**: plan.md（必須）、spec.md（必須）

**テスト**: 以下の例はテストタスクを含みます。テストはオプション - 仕様に明確に記載されている場合のみ含めます。

**組織方針**: タスクはユーザーストーリーごとにグループ化され、各ストーリーを独立して実装・テストできます。

## フォーマット：`[ID] [P?] [Story?] 説明`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 対応するユーザーストーリー（例: US1, US2, US3）
- 説明に正確なファイルパスを含める

---

## Phase 1: セットアップ（共有インフラ）

**目的**: プロジェクト初期化と基本構造

- [ ] T001 プロジェクトルートに実装計画に基づいた directory structure を作成（`rpi-wol/`, `pc-power/`, `android-client/`, `docs/`）
- [ ] T002 各コンポーネント用の `setup.py` と `requirements.txt` テンプレートを作成
- [ ] T003 [P] 各コンポーネントルートに `README.md` を作成（使用方法、セットアップ手順）
- [ ] T004 [P] プロジェクトルートに `.gitignore` を作成（Python アーティファクト除外）
- [ ] T005 `Makefile` をプロジェクトルートに作成（開発タスク: install, test, lint, run）

---

## Phase 2: 基盤インフラ（ブロッキング前提条件）

**目的**: すべてのユーザーストーリー実装前に完了が必須のコア基盤

**⚠️ 重要**: このフェーズ完了までユーザーストーリー実装は開始不可

### 共有スキーマ・通信フォーマット定義

- [ ] T006 [P] 共有スキーマモジュール `shared/` を作成（または各 `requirements.txt` で参照）
- [ ] T007 [P] API リクエスト/レスポンス JSON スキーマを定義：
  - 電源ON リクエスト: `{"target_mac": "xx:xx:xx:xx:xx:xx"}`
  - シャットダウン リクエスト: `{"timeout": 60}`
  - ステータス レスポンス: `{"status": "online|offline", "timestamp": "ISO8601"}`
  - ファイル: `shared/schemas.py` または各 component 内の `config/schemas.json`
- [ ] T008 [P] エラーレスポンス標準フォーマット定義（`{"error": "message", "code": "error_code"}`）
  - ファイル: `shared/errors.py` または `shared/constants.py`

### Raspberry Pi コンポーネント基盤

- [ ] T009 [P] `rpi-wol/` に Flask アプリスケルトン作成：
  - `src/flask_app.py` - Flask アプリケーションエントリーポイント
  - `src/config.py` - 環境変数、設定管理（RPi IP、待機ポート）
  - `src/wol_service.py` - WOL 機能の core ライブラリ（scapy 使用）

### PC コンポーネント基盤

- [ ] T010 [P] `pc-power/` に Flask アプリスケルトン作成：
  - `src/flask_app.py` - Flask アプリケーションエントリーポイント
  - `src/config.py` - 環境変数、設定管理（待機ポート、シャットダウンタイムアウト）
  - `src/power_manager.py` - PC 電源管理 core ライブラリ（OS コマンド実行）

### Android クライアント基盤

- [ ] T011 [P] `android-client/` にクライアントライブラリスケルトン作成：
  - `src/power_client.py` - REST API 通信ライブラリ（requests 使用）
  - `src/config.py` - 設定管理（Raspberry Pi IP、PC IP）
  - `src/cli.py` - CLI インターフェース定義

### 各コンポーネント共通基盤

- [ ] T012 各コンポーネントに `tests/unit/` と `tests/integration/` ディレクトリ作成
- [ ] T013 [P] 各コンポーネントの `requirements.txt` に Flask、pytest を追加
- [ ] T014 [P] 各コンポーネントの `setup.py` を設定（package 名、エントリーポイント CLI）

**チェックポイント**: 基盤準備完了 - ユーザーストーリー実装は並列で開始可能

---

## Phase 3: ユーザーストーリー 1 - Android から PC を電源ON（優先度: P1）🎯 MVP

**目標**: Android から Raspberry Pi 経由で WOL パケット送信して PC を起動

**独立テスト**: 
1. Raspberry Pi Flask サーバーを起動
2. Android クライアント（CLI or SDK）で `power_client.power_on(rpi_address, target_mac)` 呼び出し
3. Raspberry Pi ログで WOL パケット送信確認
4. PC が起動することで検証

### US1 テスト（TDD: テスト優先実装）

- [ ] T015 [P] [US1] Raspberry Pi WOL サービスの単体テスト: `rpi-wol/tests/unit/test_wol_service.py`
  - テスト内容: WOL マジックパケット生成、MAC アドレス検証、ブロードキャスト動作確認
- [ ] T016 [P] [US1] Raspberry Pi Flask エンドポイント (`/api/power/on`) の contract テスト: `rpi-wol/tests/contract/test_power_on_endpoint.py`
  - テスト内容: リクエスト形式検証、200 応答確認、レスポンス形式確認
- [ ] T017 [P] [US1] Android クライアント WOL 送信機能の単体テスト: `android-client/tests/unit/test_power_client.py`
  - テスト内容: API 呼び出し、ネットワーク通信モック、レスポンス解析

### US1 実装

- [ ] T018 [US1] Raspberry Pi WOL core ライブラリを実装: `rpi-wol/src/wol_service.py`
  - 機能: MAC アドレスからマジックパケット生成（scapy 使用）、ブロードキャスト送信
  - 入力: `target_mac`（文字列 "xx:xx:xx:xx:xx:xx" 形式）、broadcast IP
  - 出力: 成功/失敗状態、タイムスタンプ

- [ ] T019 [US1] Raspberry Pi Flask エンドポイント実装: `rpi-wol/src/flask_app.py`
  - エンドポイント: `POST /api/power/on`
  - リクエスト: `{"target_mac": "xx:xx:xx:xx:xx:xx"}`
  - レスポンス: `{"status": "packet_sent", "timestamp": "ISO8601"}`
  - 機能: リクエスト検証 → WOL サービス呼び出し → レスポンス返送

- [ ] T020 [US1] Raspberry Pi CLI インターフェース実装: `rpi-wol/src/cli.py`
  - コマンド: `power-on-rpi send-wol --mac xx:xx:xx:xx:xx:xx`
  - 出力: JSON or 人間が読める形式（成功/失敗メッセージ）

- [ ] T021 [US1] Android クライアント WOL 送信機能実装: `android-client/src/power_client.py`
  - メソッド: `PowerClient.power_on(rpi_address, target_mac)`
  - 機能: Raspberry Pi の `/api/power/on` エンドポイントに HTTP POST
  - 戻り値: 成功/失敗ステータス

- [ ] T022 [US1] Android クライアント CLI 実装 (US1 部分): `android-client/src/cli.py`
  - コマンド: `power-on-client power-on --rpi-address <ip>`
  - 出力: JSON or テキストレスポンス

- [ ] T023 [US1] エラーハンドリング・バリデーション追加
  - Raspberry Pi: 無効な MAC アドレス形式 → 400 エラー、ネットワーク失敗 → 500 エラー
  - Android クライアント: Raspberry Pi 接続失敗 → 例外スロー、タイムアウト処理

- [ ] T024 [P] [US1] 単体テスト実行・検証（T015-T017 のテストがすべてパス）
- [ ] T025 [US1] 統合テスト作成・実行: `rpi-wol/tests/integration/test_power_on_flow.py`
  - テスト内容: Flask サーバー起動 → クライアント呼び出し → WOL パケット送信確認 → サーバー停止

**チェックポイント**: US1 完全実装・テスト完了。PC 電源ON 機能は独立して動作可能

---

## Phase 4: ユーザーストーリー 2 - Android から PC を電源OFF（優先度: P1）

**目標**: Android から PC に直接接続して シャットダウンコマンド実行

**独立テスト**:
1. PC の Flask サーバーを起動
2. Android クライアントで `power_client.power_off(pc_address)` 呼び出し
3. PC がシャットダウン開始を確認

### US2 テスト（TDD: テスト優先実装）

- [ ] T026 [P] [US2] PC パワーマネジャー core の単体テスト: `pc-power/tests/unit/test_power_manager.py`
  - テスト内容: シャットダウンコマンド生成、タイムアウト設定、ステータス追跡
- [ ] T027 [P] [US2] PC Flask エンドポイント (`/api/power/shutdown`) の contract テスト: `pc-power/tests/contract/test_shutdown_endpoint.py`
  - テスト内容: リクエスト形式検証、200 応答確認、シャットダウン開始確認
- [ ] T028 [P] [US2] Android クライアント シャットダウン機能の単体テスト: `android-client/tests/unit/test_shutdown.py`
  - テスト内容: API 呼び出し、レスポンス検証

### US2 実装

- [ ] T029 [US2] PC パワーマネジャー core ライブラリを実装: `pc-power/src/power_manager.py`
  - 機能: Linux シャットダウンコマンド実行（`shutdown -h` または `systemctl poweroff`）
  - 入力: `timeout`（秒数、デフォルト 60）
  - 出力: シャットダウン状態、実行コマンド確認
  - エラー処理: 既にシャットダウン中の場合の処理

- [ ] T030 [US2] PC Flask シャットダウンエンドポイント実装: `pc-power/src/flask_app.py`
  - エンドポイント: `POST /api/power/shutdown`
  - リクエスト: `{"timeout": 60}` （オプション）
  - レスポンス: `{"status": "shutdown_initiated", "timestamp": "ISO8601"}`
  - 機能: リクエスト検証 → パワーマネジャー呼び出し → レスポンス

- [ ] T031 [US2] PC CLI インターフェース実装: `pc-power/src/cli.py`
  - コマンド: `power-on-pc shutdown --timeout 60`
  - 出力: JSON or テキスト（成功/失敗）

- [ ] T032 [US2] Android クライアント シャットダウン機能実装: `android-client/src/power_client.py`
  - メソッド: `PowerClient.power_off(pc_address, timeout=60)`
  - 機能: PC の `/api/power/shutdown` エンドポイントに HTTP POST

- [ ] T033 [US2] Android クライアント CLI 実装 (US2 部分): `android-client/src/cli.py`
  - コマンド: `power-on-client power-off --pc-address <ip> --timeout 60`

- [ ] T034 [US2] エラーハンドリング・状態管理
  - PC: 既にシャットダウン中 → 409 Conflict、コマンド実行失敗 → 500 エラー
  - Android: PC 接続失敗 → 例外スロー

- [ ] T035 [P] [US2] 単体テスト実行・検証（T026-T028）
- [ ] T036 [US2] 統合テスト作成・実行: `pc-power/tests/integration/test_shutdown_flow.py`

**チェックポイント**: US2 完全実装・テスト完了。PC 電源OFF 機能は独立して動作可能

---

## Phase 5: ユーザーストーリー 3 - Android で PC の状態を確認（優先度: P2）

**目標**: Android から PC のオンライン/オフライン状態を照会

**独立テスト**:
1. PC Flask サーバーを起動
2. Android クライアントで `power_client.status(pc_address)` 呼び出し
3. `online` または `offline` ステータス応答確認

### US3 テスト（TDD: テスト優先実装）

- [ ] T037 [P] [US3] PC ステータス取得機能の単体テスト: `pc-power/tests/unit/test_status.py`
  - テスト内容: ステータス取得、形式検証、タイムアウト処理
- [ ] T038 [P] [US3] PC Flask ステータスエンドポイント (`/api/power/status`) の contract テスト: `pc-power/tests/contract/test_status_endpoint.py`
  - テスト内容: リクエスト検証、200 応答確認、ステータス形式確認
- [ ] T039 [P] [US3] Android クライアント ステータス照会機能の単体テスト: `android-client/tests/unit/test_status.py`
  - テスト内容: API 呼び出し、ステータス解析

### US3 実装

- [ ] T040 [US3] PC ステータス取得機能を core ライブラリに追加: `pc-power/src/power_manager.py`
  - メソッド: `get_status()` → `"online"` または `"offline"`
  - 機能: 自身のオンライン状態を返す（常に `online`、PC 起動状態であることを前提）

- [ ] T041 [US3] PC Flask ステータスエンドポイント実装: `pc-power/src/flask_app.py`
  - エンドポイント: `GET /api/power/status`
  - レスポンス: `{"status": "online", "timestamp": "ISO8601"}`

- [ ] T042 [US3] PC CLI ステータスコマンド実装: `pc-power/src/cli.py`
  - コマンド: `power-on-pc status`
  - 出力: JSON or テキスト（オンライン/オフラインステータス）

- [ ] T043 [US3] Android クライアント ステータス照会機能実装: `android-client/src/power_client.py`
  - メソッド: `PowerClient.status(pc_address)` → 戻り値: `{"status": "online/offline"}`
  - 機能: PC の `/api/power/status` エンドポイントに HTTP GET

- [ ] T044 [US3] Android クライアント CLI ステータスコマンド実装: `android-client/src/cli.py`
  - コマンド: `power-on-client status --pc-address <ip>`

- [ ] T045 [US3] ステータス確認の Raspberry Pi フォールバック実装（PC が応答しない場合）
  - 機能: Android がステータス取得試行 → PC 応答ない → Raspberry Pi にフォールバック
  - Raspberry Pi は設定された PC の MAC アドレスで WOL パケット可能か判断 → `offline` 判定
  - ファイル: `android-client/src/power_client.py` に追加、`rpi-wol/src/flask_app.py` にエンドポイント追加（オプション）

- [ ] T046 [P] [US3] 単体テスト実行・検証（T037-T039）
- [ ] T047 [US3] 統合テスト作成・実行: `android-client/tests/integration/test_status_flow.py`

**チェックポイント**: US3 完全実装・テスト完了。PC ステータス確認機能は独立して動作可能

---

## Phase 6: ポーリッシュ & クロスカッティング課題

**目的**: システム全体の品質向上、ロギング、エラーハンドリング、統合テスト

### ロギング・可観測性

- [ ] T048 [P] [P] 各コンポーネントに structlogging または print-based logging 追加
  - Raspberry Pi: WOL パケット送信ログ、リクエスト受信ログ
  - PC: シャットダウン実行ログ、API リクエストログ
  - Android: API 呼び出しログ、エラーログ
  - ファイル: 各 `src/` に `logging_config.py` 追加

- [ ] T049 [P] 各コンポーネントに環境変数で LOG_LEVEL 制御を追加
  - ファイル: 各 `src/config.py` に LOG_LEVEL 環境変数追加

### エラーハンドリング・エッジケース

- [ ] T050 [P] ネットワークタイムアウト処理：
  - Android: API 呼び出し timeout = 5秒、ファイル: `android-client/src/power_client.py`
  - PC/RPi: Flask request timeout = 30秒、ファイル: 各 `src/flask_app.py`

- [ ] T051 [P] 複数コマンド並列実行時の状態管理：
  - PC: シャットダウン中に別のコマンド到着 → キューまたはエラー応答
  - ファイル: `pc-power/src/power_manager.py` に state machine 追加（オプション）

- [ ] T052 [P] 無効な入力バリデーション：
  - MAC アドレス形式検証（regex）、IP アドレス検証
  - ファイル: `shared/` または各 `src/` に validation モジュール

### システム統合テスト

- [ ] T053 エンドツーエンド統合テスト: `specs/001-pc-power-control/e2e_test.py`
  - テスト内容: 
    1. Raspberry Pi Flask サーバー起動
    2. PC Flask サーバー起動
    3. Android クライアントで power_on 呼び出し → PC 起動確認
    4. Android クライアントで status 呼び出し → online 確認
    5. Android クライアントで power_off 呼び出し → PC シャットダウン確認
    6. Android クライアントで status 呼び出し → offline 確認（またはタイムアウト）

- [ ] T054 各コンポーネント CLI コマンド統合テスト：
  - Raspberry Pi: `power-on-rpi send-wol --mac ...`
  - PC: `power-on-pc shutdown` → `power-on-pc status`
  - Android: `power-on-client power-on --rpi-address ...` など

### ドキュメント・スタートアップガイド

- [ ] T055 [P] 統合セットアップガイド作成: `docs/SETUP.md`
  - 内容: 各コンポーネント インストール、設定（IP/MAC）、実行方法

- [ ] T056 [P] API ドキュメント作成: `docs/API.md`
  - 内容: エンドポイント一覧、リクエスト/レスポンス例、エラーコード

- [ ] T057 [P] 各コンポーネント個別 README 更新（T003 の拡張）
  - 内容: 使用方法、API 仕様、テスト実行方法

### 品質チェック

- [ ] T058 [P] lint ツール実行（flake8 or black）、全 Python ファイルに適用
  - 実行: `make lint` in Makefile
- [ ] T059 [P] テストカバレッジレポート生成（pytest-cov）
  - 目標: 各コンポーネント 80% 以上
  - 実行: `make coverage`

---

## 依存関係・実行順序

```
Phase 1 (Setup)
    ↓
Phase 2 (Foundation)
    ├─→ Phase 3 (US1: Power On) ─→ Phase 5a (US1 Polish)
    ├─→ Phase 4 (US2: Power Off) ─→ Phase 5b (US2 Polish)
    └─→ Phase 5 (US3: Status) ─→ Phase 5c (US3 Polish)
        ↓
    Phase 6 (Integration & Final Polish)
```

**並列実行機会**:
- Phase 3, 4, 5 は Phase 2 完了後、互いに独立して並列実行可能
- 各フェーズ内で [P] マーク付きタスクは並列実行可能

---

## MVP（最小実現製品）スコープ

**推奨 MVP**: Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 5

これにより以下が実現されます：
- ✅ Android から Raspberry Pi 経由で PC 電源ON
- ✅ Android から PC に直接接続して電源OFF
- ✅ Android から PC ステータス確認

Phase 6 のポーリッシング・統合テストは v1.1 で実施可能。

---

## 実装戦略

1. **Phase 1-2**: 基盤セットアップ（1-2 日）
2. **Phase 3-5 並列**: 各ユーザーストーリー実装（並列で 2-3 日）
3. **Phase 6**: ポーリッシング・統合テスト（1-2 日）

**推奨開発フロー**:
- TDD を厳密に遵守（各フェーズでテストを最初に記述）
- 各 Phase 完了後に手動統合テスト
- 最後に e2e テスト実施
