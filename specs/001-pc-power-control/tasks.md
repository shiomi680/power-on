# タスク: リモートPC電源制御システム（Web UI）

**入力**: `/specs/001-pc-power-control/` の設計ドキュメント  
**前提条件**: plan.md（必須）、spec.md（必須）

**組織方針**: タスクはユーザーストーリーごとにグループ化され、各ストーリーを独立して実装・テストできます。

## フォーマット：`[ID] [P?] [Story?] 説明`

- **[P]**: 並列実行可能（異なるファイル、依存関係なし）
- **[Story]**: 対応するユーザーストーリー（例: US1, US2, US3）
- 説明に正確なファイルパスを含める

---

## Phase 1: セットアップ（共有インフラ）

**目的**: プロジェクト初期化と基本構造

- [ ] T001 プロジェクトルートに実装計画に基づいた directory structure を作成（`rpi-wol/`, `pc-power/`, `docs/`）
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
  - シャットダウン リクエスト: `{"pc_address": "xxx.xxx.xxx.xxx", "timeout": 60}`
  - ステータス レスポンス: `{"status": "online|offline", "timestamp": "ISO8601"}`
  - ファイル: `shared/schemas.py` または各 component 内の `config/schemas.json`
- [ ] T008 [P] エラーレスポンス標準フォーマット定義（`{"error": "message", "code": "error_code"}`）
  - ファイル: `shared/errors.py` または `shared/constants.py`

### Raspberry Pi コンポーネント基盤

- [ ] T009 [P] `rpi-wol/` に Flask アプリスケルトン作成：
  - `src/flask_app.py` - Flask アプリケーションエントリーポイント
  - `src/config.py` - 環境変数、設定管理（RPi IP、待機ポート）
  - `src/wol_service.py` - WOL 機能の core ライブラリ（scapy 使用）
  - `src/api/` - API エンドポイント directory 作成
  - `static/`、`templates/` directory 作成（Web UI 用）

### PC コンポーネント基盤

- [ ] T010 [P] `pc-power/` に Flask アプリスケルトン作成：
  - `src/flask_app.py` - Flask アプリケーションエントリーポイント
  - `src/config.py` - 環境変数、設定管理（待機ポート、シャットダウンタイムアウト）
  - `src/power_manager.py` - PC 電源管理 core ライブラリ（OS コマンド実行）
  - `src/api/` - API エンドポイント directory 作成

### 各コンポーネント共通基盤

- [ ] T011 各コンポーネントに `tests/unit/` と `tests/integration/` ディレクトリ作成
- [ ] T012 [P] 各コンポーネントの `requirements.txt` に Flask、pytest を追加
- [ ] T013 [P] 各コンポーネントの `setup.py` を設定（package 名、エントリーポイント CLI）

**チェックポイント**: 基盤準備完了 - ユーザーストーリー実装は並列で開始可能

---

## Phase 3: ユーザーストーリー 1 - Web UI から PC を電源ON（優先度: P1）🎯 MVP

**目標**: Web UI の電源ON ボタンから Raspberry Pi 経由で WOL パケット送信して PC を起動

**独立テスト**: 
1. Raspberry Pi Flask サーバーを起動
2. ブラウザで `http://rpi-address:5000/` にアクセス
3. Web UI から電源ON ボタンをクリック
4. Raspberry Pi ログで WOL パケット送信確認
5. PC が起動することで検証

### US1 Web UI フロントエンド

- [ ] T014 [US1] Raspberry Pi Web UI HTML テンプレート作成: `rpi-wol/templates/index.html`
  - コンテンツ: 基本的な HTML 構造、電源ON/OFF ボタン、ステータス表示エリア
  - スタイリング: 基本的な CSS（後段で `static/css/style.css` に分離）

- [ ] T015 [US1] Web UI CSS スタイル作成: `rpi-wol/static/css/style.css`
  - スタイル: ボタンのスタイリング、レスポンシブデザイン

- [ ] T016 [US1] Web UI JavaScript ロジック実装: `rpi-wol/static/js/app.js`
  - 機能: 電源ON ボタンクリック → AJAX リクエスト `/api/power/on` 送信
  - リクエスト形式: `{"target_mac": "xx:xx:xx:xx:xx:xx"}`（設定ファイルから読み込み）
  - レスポンス処理: 成功/失敗メッセージ表示

### US1 テスト（TDD: テスト優先実装）

- [ ] T017 [P] [US1] Raspberry Pi WOL サービスの単体テスト: `rpi-wol/tests/unit/test_wol_service.py`
  - テスト内容: WOL マジックパケット生成、MAC アドレス検証、ブロードキャスト動作確認
- [ ] T018 [P] [US1] Raspberry Pi Flask エンドポイント (`/api/power/on`) の contract テスト: `rpi-wol/tests/contract/test_power_on_endpoint.py`
  - テスト内容: リクエスト形式検証、200 応答確認、レスポンス形式確認
- [ ] T019 [P] [US1] Web UI の AJAX 呼び出し単体テスト: `rpi-wol/tests/unit/test_web_ui.py`（JavaScript テスト、または Jest）
  - テスト内容: ボタンクリック → API 呼び出し、レスポンス処理

### US1 バックエンド実装

- [ ] T020 [US1] Raspberry Pi WOL core ライブラリを実装: `rpi-wol/src/wol_service.py`
  - 機能: MAC アドレスからマジックパケット生成（scapy 使用）、ブロードキャスト送信
  - 入力: `target_mac`（文字列 "xx:xx:xx:xx:xx:xx" 形式）、broadcast IP
  - 出力: 成功/失敗状態、タイムスタンプ

- [ ] T021 [US1] Raspberry Pi Flask `/api/power/on` エンドポイント実装: `rpi-wol/src/api/power_on.py`
  - エンドポイント: `POST /api/power/on`
  - リクエスト: `{"target_mac": "xx:xx:xx:xx:xx:xx"}`
  - レスポンス: `{"status": "packet_sent", "timestamp": "ISO8601"}`
  - 機能: リクエスト検証 → WOL サービス呼び出し → レスポンス返送

- [ ] T022 [US1] Raspberry Pi Flask アプリにルーティング登録: `rpi-wol/src/flask_app.py`
  - 機能: `/api/power/on` ルート登録、Web UI HTML 返却（GET `/`）

- [ ] T023 [US1] Raspberry Pi CLI インターフェース実装: `rpi-wol/src/cli.py`
  - コマンド: `power-on-rpi send-wol --mac xx:xx:xx:xx:xx:xx`
  - 出力: JSON or 人間が読める形式（成功/失敗メッセージ）

- [ ] T024 [US1] エラーハンドリング・バリデーション追加
  - Raspberry Pi: 無効な MAC アドレス形式 → 400 エラー、ネットワーク失敗 → 500 エラー
  - Web UI: エラー時の UI 表示（ユーザーフレンドリーなメッセージ）

- [ ] T025 [P] [US1] 単体テスト実行・検証（T017-T019 のテストがすべてパス）
- [ ] T026 [US1] 統合テスト作成・実行: `rpi-wol/tests/integration/test_power_on_flow.py`
  - テスト内容: Flask サーバー起動 → Web ブラウザシミュレーション（requests ライブラリ）で `/api/power/on` 呼び出し → WOL パケット送信確認 → サーバー停止

**チェックポイント**: US1 完全実装・テスト完了。Web UI から PC 電源ON 機能は独立して動作可能

---

## Phase 4: ユーザーストーリー 2 - Web UI から PC を電源OFF（優先度: P1）

**目標**: Web UI の電源OFF ボタンから Raspberry Pi 経由で PC にシャットダウン API 送信

**独立テスト**:
1. PC の Flask サーバーを起動
2. ブラウザで `http://rpi-address:5000/` にアクセス
3. Web UI から電源OFF ボタンをクリック
4. PC がシャットダウン開始を確認

### US2 Web UI フロントエンド拡張

- [ ] T027 [US2] Web UI に電源OFF ボタン追加: `rpi-wol/templates/index.html`
  - UI: 電源OFF ボタンを電源ON ボタンの隣に配置

- [ ] T028 [US2] Web UI JavaScript に OFF 機能追加: `rpi-wol/static/js/app.js`
  - 機能: 電源OFF ボタンクリック → AJAX リクエスト `/api/power/shutdown` 送信
  - リクエスト形式: `{"pc_address": "xxx.xxx.xxx.xxx", "timeout": 60}`
  - レスポンス処理: 成功/失敗メッセージ表示

### US2 テスト（TDD: テスト優先実装）

- [ ] T029 [P] [US2] PC パワーマネジャー core の単体テスト: `pc-power/tests/unit/test_power_manager.py`
  - テスト内容: シャットダウンコマンド生成、タイムアウト設定、ステータス追跡
- [ ] T030 [P] [US2] PC Flask エンドポイント (`/api/power/shutdown`) の contract テスト: `pc-power/tests/contract/test_shutdown_endpoint.py`
  - テスト内容: リクエスト形式検証、200 応答確認、シャットダウン開始確認
- [ ] T031 [P] [US2] Raspberry Pi プロキシ API の単体テスト: `rpi-wol/tests/unit/test_pc_proxy.py`
  - テスト内容: PC API リクエスト送信、タイムアウト処理

### US2 バックエンド実装

- [ ] T032 [US2] PC パワーマネジャー core ライブラリを実装: `pc-power/src/power_manager.py`
  - 機能: Linux シャットダウンコマンド実行（`shutdown -h` または `systemctl poweroff`）
  - 入力: `timeout`（秒数、デフォルト 60）
  - 出力: シャットダウン状態、実行コマンド確認
  - エラー処理: 既にシャットダウン中の場合の処理

- [ ] T033 [US2] PC Flask `/api/power/shutdown` エンドポイント実装: `pc-power/src/api/shutdown.py`
  - エンドポイント: `POST /api/power/shutdown`
  - リクエスト: `{"timeout": 60}` （オプション）
  - レスポンス: `{"status": "shutdown_initiated", "timestamp": "ISO8601"}`
  - 機能: リクエスト検証 → パワーマネジャー呼び出し → レスポンス

- [ ] T034 [US2] PC Flask アプリにルーティング登録: `pc-power/src/flask_app.py`

- [ ] T035 [US2] Raspberry Pi プロキシ API 実装: `rpi-wol/src/api/pc_proxy.py`
  - 機能: Raspberry Pi が PC への HTTP リクエストをプロキシ（URL: `http://pc-address:5000/api/power/shutdown`）
  - エラーハンドリング: PC が応答しない場合のタイムアウト

- [ ] T036 [US2] Raspberry Pi Flask `/api/power/shutdown` エンドポイント実装: `rpi-wol/src/api/shutdown.py`
  - エンドポイント: `POST /api/power/shutdown`
  - リクエスト: `{"pc_address": "xxx.xxx.xxx.xxx", "timeout": 60}`
  - 機能: PC プロキシ API を呼び出し、レスポンスを返す

- [ ] T037 [US2] PC CLI シャットダウンコマンド実装: `pc-power/src/cli.py`
  - コマンド: `power-on-pc shutdown --timeout 60`
  - 出力: JSON or テキスト（成功/失敗）

- [ ] T038 [US2] エラーハンドリング・状態管理
  - PC: 既にシャットダウン中 → 409 Conflict、コマンド実行失敗 → 500 エラー
  - Raspberry Pi: PC 接続失敗 → 503 サービス利用不可、タイムアウト → 504 ゲートウェイタイムアウト
  - Web UI: エラー時の UI フィードバック

- [ ] T039 [P] [US2] 単体テスト実行・検証（T029-T031）
- [ ] T040 [US2] PC 統合テスト作成・実行: `pc-power/tests/integration/test_shutdown_flow.py`
- [ ] T041 [US2] Raspberry Pi プロキシ統合テスト: `rpi-wol/tests/integration/test_shutdown_proxy.py`

**チェックポイント**: US2 完全実装・テスト完了。Web UI から PC 電源OFF 機能は独立して動作可能

---

## Phase 5: ユーザーストーリー 3 - Web UI で PC の状態を確認（優先度: P2）

**目標**: Web UI ダッシュボードに PC のリアルタイムステータス表示

**独立テスト**:
1. PC Flask サーバーを起動
2. ブラウザで `http://rpi-address:5000/` にアクセス
3. Web UI にステータス表示を確認（オンライン/オフライン）
4. ステータスの正確性を検証

### US3 Web UI フロントエンド拡張

- [ ] T042 [US3] Web UI にステータス表示パネル追加: `rpi-wol/templates/index.html`
  - UI: ステータス表示エリア、リアルタイム更新表示（グリーン: オンライン、グレー: オフライン）

- [ ] T043 [US3] Web UI JavaScript にステータスポーリング機能追加: `rpi-wol/static/js/app.js`
  - 機能: 定期的に `/api/status` をポーリング（例: 2 秒間隔）
  - レスポンス処理: ステータス表示の更新

### US3 テスト（TDD: テスト優先実装）

- [ ] T044 [P] [US3] PC ステータス取得機能の単体テスト: `pc-power/tests/unit/test_status.py`
  - テスト内容: ステータス取得、形式検証、タイムアウト処理
- [ ] T045 [P] [US3] PC Flask ステータスエンドポイント (`/api/power/status`) の contract テスト: `pc-power/tests/contract/test_status_endpoint.py`
  - テスト内容: リクエスト検証、200 応答確認、ステータス形式確認
- [ ] T046 [P] [US3] Raspberry Pi ステータス集約機能の単体テスト: `rpi-wol/tests/unit/test_status_aggregator.py`
  - テスト内容: PC ステータス照会、キャッシング、フォールバック処理

### US3 バックエンド実装

- [ ] T047 [US3] PC ステータス取得機能を core ライブラリに追加: `pc-power/src/power_manager.py`
  - メソッド: `get_status()` → `"online"` または `"offline"`
  - 機能: 自身のオンライン状態を返す（常に `online`、PC 起動状態であることを前提）

- [ ] T048 [US3] PC Flask `/api/power/status` エンドポイント実装: `pc-power/src/api/status.py`
  - エンドポイント: `GET /api/power/status`
  - レスポンス: `{"status": "online", "timestamp": "ISO8601"}`

- [ ] T049 [US3] PC Flask アプリにルーティング登録: `pc-power/src/flask_app.py`

- [ ] T050 [US3] Raspberry Pi ステータス集約機能実装: `rpi-wol/src/api/status_aggregator.py`
  - 機能: PC の `/api/power/status` を照会、タイムアウト時のフォールバック
  - フォールバック: PC が応答しない場合 → `"offline"` と判定

- [ ] T051 [US3] Raspberry Pi Flask `/api/status` エンドポイント実装: `rpi-wol/src/api/status.py`
  - エンドポイント: `GET /api/status`
  - レスポンス: `{"status": "online/offline", "timestamp": "ISO8601"}`
  - 機能: ステータス集約機能を呼び出す

- [ ] T052 [US3] PC CLI ステータスコマンド実装: `pc-power/src/cli.py`
  - コマンド: `power-on-pc status`
  - 出力: JSON or テキスト（オンライン/オフラインステータス）

- [ ] T053 [US3] エラーハンドリング・ステータス不確定時の処理
  - ステータス取得タイムアウト → `"unknown"` 状態を返す
  - Web UI での表示: グレーまたは黄色（未確認）

- [ ] T054 [P] [US3] 単体テスト実行・検証（T044-T046）
- [ ] T055 [US3] PC ステータス統合テスト作成・実行: `pc-power/tests/integration/test_status_flow.py`
- [ ] T056 [US3] Raspberry Pi ステータスポーリング統合テスト: `rpi-wol/tests/integration/test_status_polling.py`

**チェックポイント**: US3 完全実装・テスト完了。Web UI でのステータス確認機能は独立して動作可能

---

## Phase 6: ポーリッシュ & クロスカッティング課題

**目的**: システム全体の品質向上、ロギング、エラーハンドリング、統合テスト

### ロギング・可観測性

- [ ] T057 [P] [P] 各コンポーネントに structlogging または print-based logging 追加
  - Raspberry Pi: WOL パケット送信ログ、API リクエストログ、PC プロキシログ
  - PC: シャットダウン実行ログ、API リクエストログ
  - ファイル: 各 `src/` に `logging_config.py` 追加

- [ ] T058 [P] 各コンポーネントに環境変数で LOG_LEVEL 制御を追加
  - ファイル: 各 `src/config.py` に LOG_LEVEL 環境変数追加

### エラーハンドリング・エッジケース

- [ ] T059 [P] ネットワークタイムアウト処理：
  - Raspberry Pi: PC API 呼び出し timeout = 5秒
  - 設定ファイル: `rpi-wol/src/config.py`

- [ ] T060 [P] 複数コマンド並列実行時の状態管理：
  - PC: シャットダウン中に別のコマンド到着 → キューまたはエラー応答
  - ファイル: `pc-power/src/power_manager.py` に state machine 追加（オプション）

- [ ] T061 [P] 無効な入力バリデーション：
  - MAC アドレス形式検証（regex）、IP アドレス検証、ポート番号検証
  - ファイル: `shared/` または各 `src/` に validation モジュール

### Web UI 改善

- [ ] T062 [US1+US2+US3] Web UI のレスポンシブデザイン改善：
  - CSS メディアクエリ追加（モバイル、タブレット対応）
  - ファイル: `rpi-wol/static/css/style.css`

- [ ] T063 [P] Web UI のローディング状態表示：
  - ボタンクリック時にローディングスピナー表示
  - ファイル: `rpi-wol/static/js/app.js`

- [ ] T064 [P] Web UI の設定パネル追加（オプション）：
  - PC IP、MAC アドレスの設定保存（localStorage または サーバーサイド設定）
  - ファイル: `rpi-wol/templates/config.html`、`rpi-wol/static/js/config.js`

### システム統合テスト

- [ ] T065 エンドツーエンド統合テスト: `specs/001-pc-power-control/e2e_test.py`
  - テスト内容: 
    1. Raspberry Pi Flask サーバー起動
    2. PC Flask サーバー起動
    3. Web ブラウザシミュレーション（selenium または requests）で Web UI アクセス
    4. 電源ON → PC 起動確認
    5. ステータス確認 → online 確認
    6. 電源OFF → PC シャットダウン確認
    7. ステータス確認 → offline 確認（またはタイムアウト）

- [ ] T066 各コンポーネント CLI コマンド統合テスト：
  - Raspberry Pi: `power-on-rpi send-wol --mac ...`
  - PC: `power-on-pc shutdown` → `power-on-pc status`
  - API: `curl http://rpi:5000/api/power/on` など

### ドキュメント・スタートアップガイド

- [ ] T067 [P] 統合セットアップガイド作成: `docs/SETUP.md`
  - 内容: 各コンポーネント インストール、設定（IP/MAC）、実行方法、環境変数設定

- [ ] T068 [P] API ドキュメント作成: `docs/API.md`
  - 内容: エンドポイント一覧、リクエスト/レスポンス例、エラーコード

- [ ] T069 [P] Web UI 使用ガイド作成: `docs/WEB_UI_GUIDE.md`
  - 内容: ブラウザアクセス方法、各ボタン説明、トラブルシューティング

- [ ] T070 [P] 各コンポーネント個別 README 更新（T003 の拡張）
  - 内容: 使用方法、API 仕様、テスト実行方法、設定項目説明

### 品質チェック

- [ ] T071 [P] lint ツール実行（flake8 or black）、全 Python ファイルに適用
  - 実行: `make lint` in Makefile
- [ ] T072 [P] テストカバレッジレポート生成（pytest-cov）
  - 目標: 各コンポーネント 80% 以上
  - 実行: `make coverage`

- [ ] T073 [P] Web UI パフォーマンステスト（Lighthouse または PageSpeed）
  - 目標: Lighthouse スコア 90 以上
  - ファイル: `rpi-wol/static/` 最適化

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
- 各フェーズ内で [P] マーク付きタスク（計 26 タスク）は並列実行可能

---

## MVP（最小実現製品）スコープ

**推奨 MVP**: Phase 1 + Phase 2 + Phase 3 + Phase 4 + Phase 5

これにより以下が実現されます：
- ✅ Web UI を Raspberry Pi でホスト
- ✅ Web ブラウザから PC 電源ON（WOL）
- ✅ Web ブラウザから PC 電源OFF
- ✅ Web UI でリアルタイム PC ステータス確認

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
