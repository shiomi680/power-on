# 仕様書：デプロイメント自動化 (Docker + GitHub Actions)

**機能ブランチ**: `002-deployment-automation`  
**作成日**: 2026-04-29  
**ステータス**: ドラフト  
**入力**: ユーザー説明「PC電源制御システム。Dockerでデプロイ可能にしたい。GitHub Actionsで自動テスト・ビルド・デプロイしたい。」

## ユーザーシナリオ & テスト *(必須)*

### ユーザーストーリー 1 - Docker コンテナ化（優先度: P1）

Raspberry Pi と PC のコンポーネントを Docker コンテナとして独立したマシンにデプロイしたい。各コンポーネントを別のハードウェアで実行する場合、セットアップが簡単であるべき。

**この優先度の理由**: Docker コンテナ化はデプロイメント基盤として最も重要。これがなければ自動デプロイが実現できない。

**独立テスト**: 
1. Raspberry Pi マシンで `docker compose up -d` を実行
2. PC マシンで `docker compose up -d` を実行
3. 各コンテナが起動し、API が応答することで検証完了

**受け入れ条件**:

1. **Given** Raspberry Pi に Docker・Docker Compose がインストール、**When** `docker compose up -d` を実行、**Then** Web UI がポート 5000 でアクセス可能
2. **Given** PC に Docker・Docker Compose がインストール、**When** `docker compose up -d` を実行、**Then** API がポート 5001 でアクセス可能
3. **Given** 両コンテナが起動、**When** Raspberry Pi コンテナから PC コンテナに HTTP リクエスト送信、**Then** 正常に応答を受信

---

### ユーザーストーリー 2 - CI/CD パイプライン（優先度: P1）

コード変更を push すると、自動でテスト実行→イメージビルド→レジストリにデプロイされるべき。本番環境で最新イメージを pull するだけでデプロイ可能であるべき。

**この優先度の理由**: 自動テスト・デプロイは開発効率とリリースの信頼性を大きく向上させる。本番運用に必須。

**独立テスト**:
1. コードを push
2. GitHub Actions が自動実行され、テスト実行確認
3. ビルド完了後、ghcr.io にイメージがプッシュされたことを確認
4. `docker pull ghcr.io/.../latest` で本番環境にデプロイ可能

**受け入れ条件**:

1. **Given** コードを main ブランチに push、**When** GitHub Actions ワークフローが自動実行、**Then** テストが実行されて結果が表示される
2. **Given** テストがパス、**When** ビルド完了、**Then** Docker イメージが ghcr.io に pushed される
3. **Given** v* タグを push、**When** バージョン付きイメージがビルド、**Then** `v1.0.0` など セマンティックバージョニングでプッシュされる

---

### ユーザーストーリー 3 - 本番環境デプロイの簡素化（優先度: P2）

Raspberry Pi と PC の本番環境セットアップが簡単であるべき。環境変数の設定ファイルがあり、`docker compose up -d` するだけでデプロイ完了。

**この優先度の理由**: 運用効率向上。ただし P1 機能がなければ実現しないため P2。

**独立テスト**:
1. Raspberry Pi の `.env.example` をコピーして設定
2. `docker compose up -d` 実行
3. Web UI と API が動作

**受け入れ条件**:

1. **Given** `.env.example` から `.env` をコピー、**When** PC アドレスを設定、**Then** `docker compose up -d` でデプロイ完了
2. **Given** コンテナ起動、**When** ヘルスチェック実行、**Then** 両サービスが healthy 状態

---

### エッジケース

- GitHub Actions ワークフローが失敗した場合の通知
- Docker イメージビルド失敗時の recovery
- ghcr.io への push が失敗した場合の再試行
- 複数のコンポーネントを同時にビルドする場合の並列処理
- 本番環境で古いイメージが pull されていた場合の更新確認

## 要件 *(必須)*

### 機能要件

- **FR-001**: Raspberry Pi と PC 用の独立した `docker-compose.yml` ファイルを提供
- **FR-002**: 環境変数テンプレート (`.env.example`) で主要設定項目を定義
- **FR-003**: GitHub Actions ワークフローで自動テスト実行
- **FR-004**: GitHub Actions ワークフローで Docker イメージのビルド
- **FR-005**: ビルドしたイメージを ghcr.io にプッシュ
- **FR-006**: セマンティックバージョニング対応 (v* タグでバージョン付きイメージをプッシュ)
- **FR-007**: ブランチごとのタグ付けルール（main は latest、feature ブランチは branch-sha など）
- **FR-008**: 本番環境での環境変数設定ドキュメント
- **FR-009**: Docker イメージのビルドキャッシュ保存で高速化
- **FR-010**: コンテナのヘルスチェック実装

### キーエンティティ

- **Docker イメージ**: rpi-wol, pc-power（各独立したイメージ）
- **docker-compose.yml**: Raspberry Pi 用、PC 用、開発用（各独立）
- **GitHub Actions ワークフロー**: テスト→ビルド→デプロイ（自動実行）
- **ghcr.io**: GitHub Container Registry（イメージ保存）
- **環境変数**: PC_ADDRESS, WOL_TARGET_MAC など

## 成功基準 *(必須)*

### 測定可能な成果

- **SC-001**: Docker Compose でコンテナが起動して 30 秒以内に健全な状態 (healthy) になる
- **SC-002**: GitHub Actions ワークフロー実行時間が 5 分以内に完了
- **SC-003**: テスト・ビルド・デプロイの全工程が自動で実行される
- **SC-004**: ghcr.io にプッシュされたイメージで本番環境が正常に動作（新規デプロイ時に動作確認）
- **SC-005**: main ブランチ push から ghcr.io へのプッシュまで 10 分以内に完了

## 前提条件

- Raspberry Pi と PC に Docker・Docker Compose V2 以上がインストール済み
- GitHub リポジトリが public または Container Registry 権限が設定済み
- GitHub Actions が有効化されている
- 本番環境でのネットワーク接続確認済み（Raspberry Pi ↔ PC 通信可能）

## スコープ外

- ユーザー認証・認可（LAN 内での使用を前提、v1 では範外）
- セキュリティスキャン・脆弱性チェック（オプション、v2 以降）
- Kubernetes（単純な Docker Compose で十分）
- 複数デバイスのオーケストレーション
