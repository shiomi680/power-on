# Feature Specification: Deployment README Documentation

**Feature Branch**: `003-deployment-readme`  
**Created**: 2026-04-29  
**Status**: Draft  
**Input**: User description: "デプロイ手順をREADMEに書く"

## User Scenarios & Testing *(mandatory)*

### User Story 1 - Raspberry Pi デプロイガイド (Priority: P1)

Raspberry Pi で Power-On WOL サービスをデプロイしたい開発者・運用者が、README から完全なセットアップ手順を確認できるようにする。

**Why this priority**: Raspberry Pi が本システムの核となるコンポーネントであり、デプロイが最初のステップになるため。

**Independent Test**: README の「Raspberry Pi デプロイ」セクションを読んで、実際に Raspberry Pi にクローン→セットアップ→実行が完了できることで検証。

**Acceptance Scenarios**:

1. **Given** README が存在, **When** README の Raspberry Pi セクションを読む, **Then** step-by-step でセットアップできる手順が明確に記載されている
2. **Given** 初心者ユーザー, **When** README の手順に従う, **Then** 10分以内に WOL サービスが起動できる
3. **Given** セットアップ完了後, **When** Web UI にアクセス, **Then** ポート 5000 で正常に動作している

---

### User Story 2 - PC デプロイガイド (Priority: P1)

Windows/Linux PC で Power-On 電源管理 API をデプロイしたい開発者が、README からセットアップ手順を確認できるようにする。

**Why this priority**: PC 側もシステムの重要なコンポーネントであり、同等の優先度。

**Independent Test**: README の「PC デプロイ」セクションで、実際に PC にセットアップ→実行が可能であることで検証。

**Acceptance Scenarios**:

1. **Given** README が存在, **When** README の PC セクションを読む, **Then** step-by-step でセットアップできる手順が明確に記載されている
2. **Given** 初心者ユーザー, **When** README の手順に従う, **Then** 5分以内に API サーバーが起動できる
3. **Given** セットアップ完了後, **When** API の health check endpoint にアクセス, **Then** 正常に応答している

---

### User Story 3 - Docker デプロイオプション (Priority: P1)

Docker を使った簡単デプロイを希望するユーザーが、README からコンテナ化デプロイの手順を確認できるようにする。

**Why this priority**: Docker はすでに実装されており、多くのユーザーが Docker での実行を希望するため。

**Independent Test**: README の「Docker デプロイ」セクションで、docker compose コマンドでの起動が可能であることで検証。

**Acceptance Scenarios**:

1. **Given** README が存在, **When** README の Docker セクションを読む, **Then** `docker compose up -d` で即座にデプロイできる手順が記載されている
2. **Given** Docker インストール済み環境, **When** Docker セクションの手順に従う, **Then** 2分以内に両サービスが起動できる

---

### User Story 4 - トラブルシューティング (Priority: P2)

デプロイ中に問題が発生したユーザーが、README のトラブルシューティング章で解決方法を見つけられるようにする。

**Why this priority**: ポート競合、権限エラー等の一般的な問題への対応で、ユーザー体験を大幅に向上させる。

**Independent Test**: README のトラブルシューティングセクションに、よくある問題と解決方法が記載されていることで検証。

**Acceptance Scenarios**:

1. **Given** README が存在, **When** トラブルシューティングセクションを見る, **Then** ポート競合、権限エラー、ネットワーク接続等の一般的な問題への対応が記載されている
2. **Given** デプロイ中にエラー発生, **When** README のトラブルシューティングを確認, **Then** 問題が解決できるか手がかりが得られる

---

### Edge Cases

- README が古いバージョンの情報を含んでいる場合はどうするか？(更新頻度の定義)
- 異なるOS（macOS, Windows, Linux）でのセットアップ差異をどこまでカバーするか？
- ファイアウォール、プロキシ環境でのセットアップはカバーするか？

## Requirements *(mandatory)*

### Functional Requirements

- **FR-001**: README ファイルに Raspberry Pi デプロイガイドを記載 (git clone, .env 設定, docker compose up)
- **FR-002**: README ファイルに PC デプロイガイドを記載 (git clone, .env 設定, docker compose up)
- **FR-003**: README に Docker デプロイオプションを記載 (`docker compose up -d` コマンドと使用方法)
- **FR-004**: README に前提条件（Docker, Python, SSH等）を明記
- **FR-005**: README にネットワーク設定（IP アドレス、ポート、PC_ADDRESS 環境変数）を記載
- **FR-006**: README にトラブルシューティングセクションを追加（ポート競合、権限エラー、接続不可等の解決方法）
- **FR-007**: README にクイックスタートセクションを追加（最速で動作確認できる手順）
- **FR-008**: README にシステムアーキテクチャの図またはテキスト説明を追加
- **FR-009**: README に環境変数の一覧と説明を記載
- **FR-010**: README に各セクションの目次（Table of Contents）を追加

## Success Criteria *(mandatory)*

### Measurable Outcomes

- **SC-001**: 初心者ユーザーが README だけで 15 分以内にシステムをデプロイできる
- **SC-002**: README のトラブルシューティングセクションで、よくある問題の 80% 以上がカバーされている
- **SC-003**: README の「クイックスタート」セクションで、5 分以内に動作確認ができる
- **SC-004**: README に含まれるコマンドサンプルが実行可能であり、すべてのサンプルが正常に動作する
- **SC-005**: ユーザーがデプロイ手順について追加で質問する必要がない（README で十分）

## Assumptions

- README は Markdown 形式で記述（GitHub で自動表示される）
- 既存の docs/ ディレクトリ（DOCKER.md, DEPLOYMENT.md, CI-CD.md）と重複しない内容とする
- デプロイは Linux/macOS/Windows の標準環境を想定（特殊な環境は非対象）
- Docker は v20.10 以上がインストール済みと仮定
- Python 3.10 以上がインストール済みと仮定
- ネットワーク接続とファイアウォール設定は管理者が事前対応済みと仮定
