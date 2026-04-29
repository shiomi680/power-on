# 実装計画：リモートPC電源制御システム

**ブランチ**: `001-pc-power-control` | **日付**: 2026-04-29 | **仕様**: [spec.md](spec.md)
**入力**: 機能仕様書から `/specs/001-pc-power-control/spec.md`

**注**: このテンプレートは `/speckit-plan` コマンドによって記入されます。実行ワークフローについては `.specify/templates/plan-template.md` を参照。

## 概要

Android から PC の電源を遠隔制御するシステム。3つの独立したコンポーネント：
- **Raspberry Pi WOL サービス**: Flask を使用して Android からの電源ON リクエストを受け取り、WOL マジックパケットを PC に送信
- **PC 電源管理サービス**: Flask を使用して Android からのシャットダウン・状態クエリリクエストを受け取る
- **Android クライアント**: REST API を経由して両サービスと通信

技術的アプローチ：各コンポーネントを独立したライブラリ + CLI として設計し、Library-First とテスト優先の原則に従う。

## 技術文脈

**言語/バージョン**: Python 3.10+  
**主要依存**: Flask (Web フレームワーク)、scapy (WOL パケット)、requests (HTTP 通信)  
**ストレージ**: N/A（ステートレスサービス、設定は環境変数）  
**テスト**: pytest、unittest  
**対象プラットフォーム**: Linux (Raspberry Pi, PC)  
**プロジェクトタイプ**: library/cli + distributed service  
**パフォーマンス目標**: 電源ON 応答 < 2秒、シャットダウン完了 < 30秒、状態確認応答 < 2秒  
**制約**: LAN 環境、HTTP 通信（v1 ではセキュリティ強化は範外）  
**スケール/スコープ**: シングルユーザー、少数デバイス（Android 1台、PC 1台、RPi 1台）

## 憲法チェック

*ゲート: Phase 0 研究前にパス必須。Phase 1 設計後に再チェック。*

### Principle I. 日本語優先
- **ステータス**: ✅ PASS
- **理由**: 仕様書、計画、すべてのドキュメントを日本語で記述。技術用語は原語のまま使用。

### Principle II. Library-First
- **ステータス**: ✅ PASS（設計段階で要確認）
- **要件**: 3つの独立したライブラリ + CLI
  - `power-on-rpi`: Raspberry Pi WOL サービス（ライブラリ + CLI）
  - `power-on-pc`: PC シャットダウン/状態管理（ライブラリ + CLI）
  - `power-on-android`: Android クライアント（ライブラリ + CLI）
- **確認**: 各コンポーネントは自己完結、独立テスト可能、ドキュメント化

### Principle III. CLI Interface
- **ステータス**: ✅ PASS（設計段階で要確認）
- **要件**: 各ライブラリは CLI インターフェースを公開
  - stdin/args → stdout、エラー → stderr
  - JSON + 人間が読める形式

### Principle IV. テスト優先（MUST）
- **ステータス**: ✅ PASS（実装段階で厳格に遵守）
- **要件**: TDD 必須、Red-Green-Refactor サイクル厳守
- **計画**: 各モジュールの単体テスト + 統合テスト

### Principle V. 統合テスト重視
- **ステータス**: ✅ PASS（設計段階で要確認）
- **重視領域**:
  - サービス間通信テスト（Android ↔ RPi、Android ↔ PC）
  - WOL パケット送受信テスト
  - ステータス形式・コマンド形式の共有スキーマテスト

**初期ゲート評価**: すべてパス。Phase 0 進行可能。

## プロジェクト構造

### ドキュメント（この機能）

```text
specs/001-pc-power-control/
├── plan.md              # このファイル（/speckit-plan コマンド出力）
├── research.md          # Phase 0 出力（/speckit-plan コマンド）
├── data-model.md        # Phase 1 出力（/speckit-plan コマンド）
├── quickstart.md        # Phase 1 出力（/speckit-plan コマンド）
├── contracts/           # Phase 1 出力（/speckit-plan コマンド）
├── checklists/          # 品質チェックリスト
└── tasks.md             # Phase 2 出力（/speckit-tasks コマンド）
```

### ソースコード（リポジトリルート）

```text
power-on/                          # リポジトリルート
├── rpi-wol/                       # Raspberry Pi WOL サービス（ライブラリ + CLI）
│   ├── src/
│   │   ├── wol_service.py         # WOL コア機能ライブラリ
│   │   ├── flask_app.py           # Flask アプリケーション
│   │   ├── cli.py                 # CLI インターフェース
│   │   └── config.py              # 設定管理
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_wol_service.py
│   │   │   └── test_config.py
│   │   ├── integration/
│   │   │   ├── test_flask_app.py
│   │   │   └── test_wol_communication.py
│   │   └── contract/
│   │       └── test_api_contract.py
│   ├── setup.py
│   └── requirements.txt
│
├── pc-power/                      # PC 電源管理サービス（ライブラリ + CLI）
│   ├── src/
│   │   ├── power_manager.py       # PC シャットダウン/状態管理ライブラリ
│   │   ├── flask_app.py           # Flask アプリケーション
│   │   ├── cli.py                 # CLI インターフェース
│   │   └── config.py              # 設定管理
│   ├── tests/
│   │   ├── unit/
│   │   │   ├── test_power_manager.py
│   │   │   └── test_config.py
│   │   ├── integration/
│   │   │   ├── test_flask_app.py
│   │   │   └── test_shutdown_command.py
│   │   └── contract/
│   │       └── test_api_contract.py
│   ├── setup.py
│   └── requirements.txt
│
├── android-client/                # Android クライアント（ライブラリ + CLI）
│   ├── src/
│   │   ├── power_client.py        # リモート制御クライアントライブラリ
│   │   ├── cli.py                 # CLI インターフェース（デバッグ用）
│   │   └── config.py              # 設定管理
│   ├── tests/
│   │   ├── unit/
│   │   │   └── test_power_client.py
│   │   └── integration/
│   │       └── test_end_to_end.py
│   ├── setup.py
│   └── requirements.txt
│
├── docs/                          # プロジェクトドキュメント
│   ├── README.md
│   ├── SETUP.md                   # セットアップガイド
│   └── API.md                     # API 仕様書
│
├── specs/                         # 仕様とプラン
│   └── 001-pc-power-control/
│
└── Makefile                       # 開発タスク
```

**構造の決定理由**:
- 3つの独立したコンポーネントを separate directories として実装
- 各コンポーネントは Library-First 原則に従い、自立したパッケージ構成
- 共有コード（スキーマ、ヘルパー）は後段で `shared/` または individual requirements.txt でピンされた共通ライブラリとして管理
- CLI インターフェース: 各ライブラリの `cli.py` で実装、`setup.py` のエントリーポイントで公開

## 複雑性トラッキング

> **憲法チェックに違反がある場合のみ記入（正当化が必要）**

**評価**: 違反なし。複雑性トラッキング不要。

---

## Phase 0: 調査・研究

### NEEDS CLARIFICATION の特定と解決

技術文脈セクションの検討：
- ✅ 言語：Python 3.10+ （Flask が指定されているため明確）
- ✅ 依存：Flask、scapy、requests （仕様から明確）
- ✅ テスト：pytest （Python プロジェクト標準）
- ✅ プラットフォーム：Linux （RPi、PC 指定）
- ✅ パフォーマンス：仕様で定義済み

**研究タスク**:
1. Python での WOL マジックパケット送信ベストプラクティス（scapy 使用）
2. Flask での REST API テスト戦略
3. マルチサービス統合テストのベストプラクティス
4. Android から Python API への通信パターン

**出力**: research.md（次段階で生成）

---

## Phase 1: 設計・コントラクト定義

### 1. データモデル抽出

**主要エンティティ**:
- **デバイス**: Android、PC、Raspberry Pi
- **コマンド**: PowerOn（RPi宛）、PowerOff（PC宛）、StatusQuery（PC宛）
- **レスポンス**: Status（online/offline）、CommandResult（success/error）

**状態遷移** (PC):
- offline → (WOL パケット受信) → online
- online → (Shutdown コマンド受信) → shutting_down → offline

**出力**: data-model.md（次段階で生成）

### 2. インターフェースコントラクト

3つのコンポーネントが公開するコントラクト：

**Raspberry Pi WOL サービス**:
- **エンドポイント**: POST `/api/power/on`
- **リクエスト**: `{"target_mac": "xx:xx:xx:xx:xx:xx"}`
- **レスポンス**: `{"status": "packet_sent", "timestamp": "ISO8601"}`

**PC パワーマネジャーサービス**:
- **エンドポイント 1**: POST `/api/power/shutdown`
  - **リクエスト**: `{"timeout": 60}`
  - **レスポンス**: `{"status": "shutdown_initiated", "timestamp": "ISO8601"}`
- **エンドポイント 2**: GET `/api/power/status`
  - **レスポンス**: `{"status": "online/offline", "uptime": "seconds"}`

**CLI インターフェース** (各コンポーネント):
```bash
# RPi
$ power-on-rpi --help
  power-on-rpi send-wol --mac xx:xx:xx:xx:xx:xx

# PC
$ power-on-pc --help
  power-on-pc shutdown --timeout 60
  power-on-pc status

# Android
$ power-on-client --help
  power-on-client power-on --rpi-address <ip>
  power-on-client power-off --pc-address <ip>
  power-on-client status --pc-address <ip>
```

**出力**: contracts/ ディレクトリ（次段階で生成）

### 3. クイックスタート

セットアップと基本的な使用例。

**出力**: quickstart.md（次段階で生成）

### 4. CLAUDE.md 更新

計画ファイルへの参照を更新。

---

## 計画完成

**ブランチ**: 001-pc-power-control
**計画ファイル**: specs/001-pc-power-control/plan.md
**次のステップ**: `/speckit-tasks` で実装タスク生成、または `/speckit-analyze` で仕様・計画・タスク間の整合性確認
