<!-- 
CONSTITUTION SYNC REPORT
Version: 0.1.0 → 1.0.0 (MINOR: Initial constitution with 5 principles)
Date: 2026-04-29
Changes:
  - Added I. 日本語優先 (Japanese-first principle)
  - Customized II. Library-First with Japanese description
  - Customized III. CLI Interface with Japanese description
  - Customized IV. テスト優先 (Test-first principle)
  - Customized V. 統合テスト重視 (Integration testing principle)
  - Updated Governance section with amendment procedures
Templates to update: spec-template.md, plan-template.md, tasks-template.md (verify compatibility)
-->

# Power-On Project Constitution

**プロジェクト概要**: PC電源制御システム（Android/Raspberry Pi/PC統合制御）

## Core Principles

### I. 日本語優先

すべてのドキュメント、コメント、コミットメッセージは日本語で記述します。技術用語やブランド名（Flask、WOL、HTTP等）は原語のまま使用可能です。これにより、プロジェクトの保守性と理解度を高めます。

**適用範囲**: README、ドキュメント、コード内コメント、Git コミットメッセージ、PR説明、Issue説明

### II. Library-First

すべての機能は独立したライブラリから始まります。各ライブラリは以下の要件を満たす必要があります：

- 自己完結型：外部依存を最小化、明確に定義
- 独立してテスト可能：ユニットテスト、統合テストが可能
- ドキュメント化：使用方法、API仕様、制約事項を明記
- 明確な目的：組織的役割だけのライブラリは不可

### III. CLI Interface

すべてのライブラリは CLI インターフェースを公開します。以下を遵守します：

- **テキスト I/O プロトコル**: stdin/args → stdout、エラー → stderr
- **形式サポート**: JSON形式（プログラム利用）+ 人間が読める形式（人間利用）
- **エラーハンドリング**: 明確なエラーメッセージ、適切な終了コード

### IV. テスト優先（MUST）

TDD（Test-Driven Development）は必須です：

1. テストを記述
2. ユーザー承認を得る
3. テストが失敗することを確認
4. 実装する

**Red-Green-Refactor サイクル**を厳密に遵守します。テスト抜きの実装は許可されません。

### V. 統合テスト重視

以下の領域では統合テストを重視します：

- 新規ライブラリのコントラクトテスト
- コントラクト変更（API/仕様の変更）
- サービス間通信（Android ↔ Raspberry Pi ↔ PC）
- 共有スキーマ（ステータス形式、コマンド形式等）

## Development Workflow

- **ブランチ命名**: `NNN-feature-name` または `YYYYMMDD-HHMMSS-feature-name`
- **Spec → Plan → Tasks → Implementation** ワークフローを遵守
- 各フェーズで日本語ドキュメントを更新

## Governance

この憲法はプロジェクトのすべての実践に優先されます。

**修正手続き**:
- 修正は新しいコミットとして記録
- バージョン番号は Semantic Versioning に従う
  - MAJOR: 後方互換性を欠く変更（プリンシプルの削除・再定義）
  - MINOR: 新プリンシプル追加、既存プリンシプル拡張
  - PATCH: 説明の明確化、タイポ修正、非セマンティック改善
- すべての PR/レビュー時に遵守状況を確認

**Version**: 1.0.0 | **Ratified**: 2026-04-29 | **Last Amended**: 2026-04-29
