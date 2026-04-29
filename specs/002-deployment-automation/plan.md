# Implementation Plan: Deployment Automation

**Branch**: `002-deployment-automation` | **Date**: 2026-04-29 | **Spec**: specs/002-deployment-automation/spec.md
**Input**: Feature specification from `/specs/002-deployment-automation/spec.md`

**Note**: This template is filled in by the `/speckit-plan` command. See `.specify/templates/plan-template.md` for the execution workflow.

## Summary

Docker コンテナ化により、Raspberry Pi と PC コンポーネントを独立したハードウェアにデプロイ可能にする。GitHub Actions ワークフローで自動テスト・イメージビルド・ghcr.io へのプッシュを実現し、本番環境での `docker compose up -d` による簡単デプロイを実現する。

## Technical Context

**Language/Version**: Python 3.10+ (既存コンポーネント使用)  
**Primary Dependencies**: Docker, Docker Compose V2, GitHub Actions, ghcr.io (GitHub Container Registry)  
**Storage**: N/A (デプロイメント基盤)  
**Testing**: pytest (既存フレームワーク、ワークフローで自動実行)  
**Target Platform**: Linux/Docker (Raspberry Pi, PC, GitHub Actions runner)  
**Project Type**: Deployment Infrastructure (Container Orchestration)  
**Performance Goals**: ワークフロー実行時間 < 5 分、コンテナ起動 < 30 秒  
**Constraints**: Docker Compose V2 互換性、ghcr.io との互換性、セマンティックバージョニング対応  
**Scale/Scope**: 2 コンポーネント (rpi-wol, pc-power)、matrix ビルド対応

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-check after Phase 1 design.*

**原則 I. 日本語優先**: ✓ 仕様書・ドキュメントは日本語で記述

**原則 II. Library-First**: ✓ Docker コンテナは既存の独立ライブラリをラップ（wol_service, power_manager）

**原則 III. CLI Interface**: 部分適用 - コンテナ化対象はCLIインターフェース実装済み

**原則 IV. テスト優先**: ✓ ワークフローでテスト実行が必須（テスト失敗時はビルドをスキップ）

**原則 V. 統合テスト重視**: ✓ ワークフロー実行時の統合テスト（コンテナ間通信）必須

**ゲート評価**: PASS - すべての原則が整合している

## Project Structure

### Documentation (this feature)

```text
specs/002-deployment-automation/
├── plan.md              # This file (/speckit-plan command output)
├── research.md          # Phase 0 output (/speckit-plan command)
├── data-model.md        # Phase 1 output (/speckit-plan command)
├── quickstart.md        # Phase 1 output (/speckit-plan command)
├── contracts/           # Phase 1 output (/speckit-plan command)
└── tasks.md             # Phase 2 output (/speckit-tasks command)
```

### Source Code (repository root)

```text
# Deployment Infrastructure
rpi-wol/
├── Dockerfile           # Raspberry Pi コンテナイメージ定義
├── docker-compose.yml   # 本番用 (Raspberry Pi 単体)
├── .env.example         # 環境変数テンプレート
├── src/
│   ├── wol_service.py   # WOL ライブラリ
│   ├── power_manager.py # (利用不可)
│   ├── flask_app.py     # Flask アプリ
│   ├── api/
│   │   ├── power_on.py
│   │   ├── status.py
│   │   └── shutdown.py
│   ├── templates/
│   └── static/
├── tests/
│   ├── unit/
│   ├── contract/
│   └── integration/
└── requirements.txt

pc-power/
├── Dockerfile           # PC コンテナイメージ定義
├── docker-compose.yml   # 本番用 (PC 単体)
├── .env.example         # 環境変数テンプレート
├── src/
│   ├── power_manager.py # 電源管理ライブラリ
│   ├── flask_app.py     # Flask API サーバー
│   ├── api/
│   │   ├── shutdown.py
│   │   └── status.py
├── tests/
│   ├── unit/
│   ├── contract/
│   └── integration/
└── requirements.txt

docker-compose.yml       # 開発環境用 (両コンポーネント)
.dockerignore           # Docker ビルド除外

.github/workflows/
├── docker-publish.yml   # CI/CD ワークフロー
└── README.md           # ワークフロー説明

docs/
├── CI-CD.md             # CI/CD ガイド
├── DOCKER.md            # Docker デプロイメントガイド
└── DEPLOYMENT.md        # 統合デプロイメントガイド
```

**Structure Decision**: 既存の 2 コンポーネント構造を維持。各コンポーネントに独立した Dockerfile と docker-compose.yml を配置。GitHub Actions ワークフローで matrix ビルドにより並列処理。

## Phase 0: Research & Decisions

**研究項目**: なし - Docker・GitHub Actions の実装は既に完了しており、ワークフロー・Dockerfile の設計は検証済み。

**決定事項**:
- **マトリックスビルド**: GitHub Actions の strategy.matrix で rpi-wol と pc-power を並列ビルド
- **イメージレジストリ**: ghcr.io (GitHub Container Registry) を使用
- **タグ付けルール**: main ブランチ → latest, feature ブランチ → branch-sha, v* タグ → セマンティックバージョニング
- **キャッシュ戦略**: registry キャッシュを使用して buildx でビルド高速化

## Phase 1: Design Documents

以下のドキュメントを作成予定：

1. **data-model.md**: Docker イメージ、コンテナ、レジストリエントリの定義
2. **quickstart.md**: ローカル開発デプロイ、本番環境デプロイの手順
3. **contracts/**: GitHub Actions ワークフロー入出力の仕様（オプション）

## Implementation Phases (Tasks)

Phase 2 で詳細なタスク分解を `/speckit-tasks` で実施

| ユーザーストーリー | 優先度 | 説明 |
|-----------------|--------|------|
| US1: Docker コンテナ化 | P1 | 独立した docker-compose.yml、環境変数テンプレート |
| US2: CI/CD パイプライン | P1 | GitHub Actions ワークフロー、自動テスト・ビルド・デプロイ |
| US3: デプロイ簡素化 | P2 | .env.example、ヘルスチェック実装、デプロイドキュメント |
