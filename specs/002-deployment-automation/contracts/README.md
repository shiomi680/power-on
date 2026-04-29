# Contracts (Deployment Automation)

## 概要

このディレクトリは、デプロイメント自動化機能の外部インターフェース契約を管理するための場所です。

## 現状

**現在、このディレクトリは空です。**

理由: デプロイメント自動化は内部インフラストラクチャ機能です。以下のエンティティは既存コンポーネント（rpi-wol, pc-power）の内部仕様であり、新しい外部契約は定義されていません：

- Docker イメージメタデータ: `data-model.md` で定義
- Docker Compose スキーマ: `data-model.md` で定義
- GitHub Actions ワークフロー設定: `.github/workflows/docker-publish.yml` で定義

## 将来の契約（Phase 3+）

以下の場合、このディレクトリに契約を追加します：

- **REST API**: ghcr.io との通信プロトコル（実装不要、既存の docker CLI で対応）
- **Webhook**: GitHub Actions イベントから外部システムへの通知（Phase 3 で検討）
- **レジストリ API**: イメージプッシュ・プル時の認証・メタデータ交換（GitHub が管理）

現時点では、これらは既存の標準仕様に従うため、独自契約の定義は不要です。
