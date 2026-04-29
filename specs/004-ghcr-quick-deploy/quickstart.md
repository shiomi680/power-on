# クイックスタート・シナリオ: ghcr.io ワンコマンド・デプロイメント

**日付**: 2026-04-29  
**入力**: spec.md のユーザーストーリー、research.md の決定事項

このドキュメントは、3 つの主要なデプロイメント・シナリオを提示し、各シナリオの実行手順、期待される出力、検証方法を記載します。

---

## シナリオ 1: Git Clone（推奨・初心者向け）

**所要時間**: 5-10 分  
**対象ユーザー**: すべてのユーザー（初心者から開発者まで）  
**前提条件**: Docker v20.10+、git、インターネット接続

### ユースケース
> 開発者が git clone でリポジトリ全体を取得し、ドキュメント確認後、docker compose で起動したい。

### 手順

#### ステップ 1: Git リポジトリをクローン

```bash
git clone https://github.com/shiomi680/power-on.git
cd power-on
```

**期待される出力**:
```
Cloning into 'power-on'...
remote: Enumerating objects: 150, done.
...
```

**検証**:
```bash
ls -la
# README.md, docker-compose.yml, rpi-wol/, pc-power/, .github/ 等が存在
```

#### ステップ 2: .env ファイルを設定

```bash
cp .env.example .env

# 環境に応じて編集
nano .env
```

#### ステップ 3: ドキュメント確認（オプション）

```bash
# README.md でデプロイメント・ガイドを確認
cat README.md | grep -A 20 "## デプロイメント"

# アーキテクチャを確認
cat docs/ARCHITECTURE.md
```

#### ステップ 4: Docker Compose で起動

```bash
# root の docker-compose.yml で両サービスを起動
docker compose up -d

# または個別にスタンドアロン・デプロイ
# docker compose -f rpi-wol/docker-compose.yml up -d
# docker compose -f pc-power/docker-compose.yml up -d
```

#### ステップ 5: ヘルスチェック検証

```bash
docker compose ps
curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
```

### 成功基準

- [ ] git clone が成功している
- [ ] README、ARCHITECTURE が読める
- [ ] docker compose up -d でエラーなく起動
- [ ] ヘルスチェックが正常に応答

---

## シナリオ 2: バージョン・ピン指定（本番デプロイメント）

**所要時間**: 5 分  
**対象ユーザー**: 本番運用者  
**前提条件**: Docker v20.10+、docker-compose.yml ファイル（Release assets から取得）

### ユースケース
> 本番運用者が特定の検証済みイメージバージョンをピン指定してデプロイし、再現性を確保したい。

### 手順

#### ステップ 1: Release assets から docker-compose.yml を取得

```bash
# 例: v1.0.0 を使用（release assets はこのバージョンに対応）
curl -L -o docker-compose.yml \
  https://github.com/shiomi680/power-on/releases/download/v1.0.0/docker-compose.yml

# バージョンをピン指定であることを確認
grep "image:" docker-compose.yml
# Expected:
# image: ghcr.io/shiomi680/power-on-rpi:v1.0.0
# image: ghcr.io/shiomi680/power-on-pc:v1.0.0
```

#### ステップ 2: 異なるバージョンを試す（オプション）

```bash
# 別のバージョンに切り替える場合（例: v1.1.0）
# URL の v1.0.0 を v1.1.0 に変更してダウンロード
curl -L -o docker-compose.yml \
  https://github.com/shiomi680/power-on/releases/download/v1.1.0/docker-compose.yml

grep "image:" docker-compose.yml
# Expected:
# image: ghcr.io/shiomi680/power-on-rpi:v1.1.0
# image: ghcr.io/shiomi680/power-on-pc:v1.1.0
```

#### ステップ 3: 本番環境に対応するバージョンで起動

```bash
docker compose up -d

# ログ確認（バージョンが正しいことを確認）
docker logs power-on-rpi | grep "version"
```

### 成功基準

- [ ] Release assets から docker-compose.yml が取得できる
- [ ] docker-compose.yml に具体的なバージョン・タグ（例: v1.0.0）が含まれている
- [ ] docker compose up -d でピン指定バージョンのイメージが起動される
- [ ] ヘルスチェックが正常に応答

---

## シナリオ 3: ローカル・ビルド（開発・カスタマイズ）

**所要時間**: 10 分  
**対象ユーザー**: 開発者、カスタマイズ希望者  
**前提条件**: Docker v20.10+、git、build tools、ソースコード

### ユースケース
> 開発者がコード修正後、ローカル・ビルド・オプションで独自イメージを作成・テストしたい。

### 手順

#### ステップ 1: Git クローン + ソースコード確認

```bash
git clone https://github.com/shiomi680/power-on.git
cd power-on
```

#### ステップ 2: ローカル・ビルド・オプション用 docker-compose.local.yml を作成

```yaml
# docker-compose.local.yml
version: '3.8'

services:
  rpi-wol:
    build:
      context: ./rpi-wol
      dockerfile: Dockerfile
    container_name: power-on-rpi-dev
    ports:
      - "5000:5000"
    environment:
      - PC_ADDRESS=${PC_ADDRESS:-192.168.1.100}
      - WOL_TARGET_MAC=${WOL_TARGET_MAC:-aa:bb:cc:dd:ee:ff}
      # ... other env vars
    restart: unless-stopped

  pc-power:
    build:
      context: ./pc-power
      dockerfile: Dockerfile
    container_name: power-on-pc-dev
    ports:
      - "5001:5001"
    environment:
      - SHUTDOWN_TIMEOUT=${SHUTDOWN_TIMEOUT:-60}
      # ... other env vars
    restart: unless-stopped
```

#### ステップ 3: .env を設定

```bash
cp .env.example .env
# (必要に応じて編集)
```

#### ステップ 4: ローカル・ビルド + 起動

```bash
# docker-compose.local.yml を使用してビルド・起動
docker compose -f docker-compose.local.yml up -d --build

# または個別にビルド
docker build -t power-on-rpi:dev ./rpi-wol
docker build -t power-on-pc:dev ./pc-power
docker compose -f docker-compose.local.yml up -d
```

**期待される出力** (ビルド中):
```
[+] Building 12.5s (8/8) FINISHED
 => [rpi-wol] importing cache manifest from docker.io/...
 => [rpi-wol] exporting to image
 => => naming to docker.io/library/power-on-rpi:dev
```

#### ステップ 5: ローカル・イメージで起動確認

```bash
docker ps
# Expected:
# power-on-rpi-dev    Running
# power-on-pc-dev     Running

curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
```

### 成功基準

- [ ] docker build コマンドが成功している
- [ ] docker-compose.local.yml でローカル・イメージが起動されている
- [ ] ログに build info が表示されている
- [ ] ヘルスチェックが正常に応答

---

## 統合検証チェックリスト

すべてのシナリオで以下を検証してください：

- [ ] **イメージ取得**: docker pull / docker build が成功している
- [ ] **コンテナ起動**: docker compose up -d でエラーなく起動
- [ ] **2 分以内起動**: ヘルスチェック応答まで 2 分以内（SC-002）
- [ ] **ヘルスチェック**: /api/health エンドポイントが 200 OK
- [ ] **ネットワーク通信**: rpi-wol ↔ pc-power 間で通信可能
- [ ] **ログ出力**: docker logs で正常なログが記録されている
- [ ] **リソース**: メモリ、CPU 使用率が適正範囲（通常負荷 <500MB）

