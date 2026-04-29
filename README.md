# Power-On: リモート PC 電源制御システム

[![GitHub Actions: CI/CD](https://github.com/shiomi680/power-on/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/shiomi680/power-on/actions)
[![Container Registry](https://img.shields.io/badge/registry-ghcr.io-blue)](https://github.com/shiomi680/power-on/pkgs/container/)

Raspberry Pi から PC の電源状態を制御する Wake-on-LAN（WOL）・電源管理システム。Docker によるマルチプラットフォーム対応でデプロイ可能。

## 目次

- [クイックスタート（5 分）](#クイックスタート---ghcrioプリビルトイメージデプロイ)
- [本番環境でのバージョン・ピン指定](#本番環境でのバージョンピン指定)
- [開発・カスタマイズ（ローカル・ビルド）](#開発カスタマイズローカルビルド)
- [前提条件](#前提条件)
- [アーキテクチャ概要](#アーキテクチャ概要)
- [デプロイメントガイド](#デプロイメントガイド)
  - [Raspberry Pi WOL サービス](#raspberry-pi-wol-サービス)
  - [PC 電源制御 API](#pc-電源制御-api)
  - [Docker デプロイメント](#docker-デプロイメント)
- [環境変数](#環境変数)
- [トラブルシューティング](#トラブルシューティング)
- [関連ドキュメント](#関連ドキュメント)

---

## クイックスタート - ghcr.io プリビルト・イメージ・デプロイ

**所要時間**: 5-10 分  
**前提**: Docker v20.10+、git がインストール済み

### ステップ 1: リポジトリをクローン

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

**確認**:
```bash
ls -la
# README.md, docker-compose.yml, rpi-wol/, pc-power/, .github/ が存在
```

### ステップ 2: 環境変数を設定

```bash
cp .env.example .env

# 環境に応じて編集
nano .env
```

**必須変数**（.env 内に編集）:
- `PC_ADDRESS`: 対象 PC の IP アドレス（例: 192.168.1.100）
- `WOL_TARGET_MAC`: 対象 PC の MAC アドレス（例: aa:bb:cc:dd:ee:ff）

### ステップ 3: Docker Compose で起動

```bash
docker compose up -d

# コンテナ状態を確認
docker compose ps
```

**期待される出力**:
```
NAME              COMMAND              SERVICE      STATUS
power-on-rpi      python -m ...        rpi-wol      Up
power-on-pc       python -m ...        pc-power     Up
```

### ステップ 4: ヘルスチェック（2 分以内に応答）

```bash
curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
```

**期待される応答**: HTTP 200 OK

### 検証チェックリスト（テスト仕様）

- [ ] git clone が成功し、README.md、docker-compose.yml、rpi-wol/、pc-power/ が存在
- [ ] .env ファイルが作成・編集可能
- [ ] docker compose ps で両コンテナが Running 状態
- [ ] curl http://localhost:5000/api/health が 200 OK を返す
- [ ] curl http://localhost:5001/api/health が 200 OK を返す
- [ ] 2 分以内に起動完了

---

## 本番環境でのバージョン・ピン指定

本番運用では、特定の検証済みイメージバージョンをピン指定して再現性を確保します。

### ステップ 1: docker-compose.yml のバージョンを確認

```bash
grep "image:" docker-compose.yml
```

**期待される出力**:
```
image: ghcr.io/shiomi680/power-on-rpi:v1.0.0
image: ghcr.io/shiomi680/power-on-pc:v1.0.0
```

### ステップ 2: バージョンを切り替える場合

```bash
# docker-compose.yml を編集してバージョンを変更
# 例: v1.0.0 → v1.1.0

# イメージを再取得して起動
docker compose pull
docker compose up -d
```

### ステップ 3: バージョン確認

```bash
docker compose ps
docker inspect power-on-rpi | grep "Image:"
docker inspect power-on-pc | grep "Image:"
```

### 本番環境検証チェックリスト

- [ ] docker-compose.yml に具体的なバージョン・タグ（v1.0.0 等）が指定されている
- [ ] docker compose pull が指定バージョンのイメージを取得
- [ ] docker inspect でイメージバージョンが正しいことを確認
- [ ] バージョン切り替え後、両コンテナが起動可能

---

## 開発・カスタマイズ（ローカル・ビルド）

コード修正後、ローカルで独自イメージをビルド・テストします。

### ステップ 1: ソースコードを確認

```bash
git clone https://github.com/shiomi680/power-on.git
cd power-on
```

### ステップ 2: ローカル・ビルド用 docker-compose ファイルを作成

```bash
cat > docker-compose.local.yml << 'EOF'
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
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5000
      - PC_ADDRESS=${PC_ADDRESS:-192.168.1.100}
      - WOL_TARGET_MAC=${WOL_TARGET_MAC:-aa:bb:cc:dd:ee:ff}
      - WOL_BROADCAST_IP=${WOL_BROADCAST_IP:-255.255.255.255}
    restart: unless-stopped

  pc-power:
    build:
      context: ./pc-power
      dockerfile: Dockerfile
    container_name: power-on-pc-dev
    ports:
      - "5001:5001"
    environment:
      - FLASK_HOST=0.0.0.0
      - FLASK_PORT=5001
      - SHUTDOWN_TIMEOUT=60
    restart: unless-stopped
EOF
```

### ステップ 3: .env を設定

```bash
cp .env.example .env
nano .env  # 必要に応じて編集
```

### ステップ 4: ローカル・ビルド + 起動

```bash
# docker-compose.local.yml でビルド・起動
docker compose -f docker-compose.local.yml up -d --build

# または個別にビルド
docker build -t power-on-rpi:dev ./rpi-wol
docker build -t power-on-pc:dev ./pc-power
docker compose -f docker-compose.local.yml up -d
```

### ステップ 5: 確認

```bash
docker compose -f docker-compose.local.yml ps

curl http://localhost:5000/api/health
curl http://localhost:5001/api/health
```

### 開発環境検証チェックリスト

- [ ] docker build コマンドが成功
- [ ] docker-compose.local.yml でローカル・イメージが起動
- [ ] curl ヘルスチェック が 200 OK を返す

---

## 前提条件

### システム要件

| コンポーネント | 要件 | 備考 |
|------------|------|------|
| **CPU** | 64 ビットプロセッサ | Raspberry Pi 3B+ 以上推奨 |
| **RAM** | 最小 2GB | 4GB 以上推奨 |
| **ストレージ** | 4GB 以上の空き容量 | OS・Docker インストール後 |
| **ネットワーク** | Ethernet または WiFi | 対象 PC と同じ LAN 上 |

### ソフトウェア要件

| ソフトウェア | バージョン | インストール |
|----------|-----------|-----------|
| **Docker** | v20.10 以上 | [Docker インストールガイド](https://docs.docker.com/get-docker/) |
| **Docker Compose** | v2.0 以上（V2 のみ） | Docker Desktop に付属 |
| **Git** | 最新版 | `sudo apt install git`（Linux/RPi） |
| **Python** | 3.10 以上（ネイティブデプロイ時のみ） | ほとんどのシステムにプレインストール |

### ネットワーク要件

| 項目 | 要件 | 備考 |
|-----|------|------|
| **WOL ポート** | UDP 5000 またはカスタム | 通常はブロードキャストアドレス |
| **ファイアウォール** | UDP ブロードキャスト許可 | WOL マジックパケット用 |
| **PC ポート** | TCP 5001 またはカスタム | 電源制御 API 通信用 |
| **サブネット** | 対象 PC と同じ LAN | WOL は同じブロードキャストドメイン必須 |

### ハードウェア固有の注記

**Raspberry Pi の場合**:
- Ethernet 接続を強く推奨（WiFi より）
- 低メモリシステム（Pi Zero/Zero2）では docker-compose.yml の調整が必要な場合あり
- Systemd サービス設定で起動時の自動開始可能

**Windows PC の場合**:
- BIOS で「Wake-On-LAN」を有効化必須
- Windows Defender が電源制御 API ポートをブロック可能性あり
- Windows Server 実行時は「ネットワークインターフェース」ハードウェアアクセスを有効化必須

---

## アーキテクチャ概要

```
┌─────────────────────────────────────────────┐
│         ユーザー / 管理者                    │
│                                             │
│  Web ブラウザ          システム CLI          │
│  (http://rpi:5000)    (docker, ssh 等)    │
└────────────────┬────────────────────────────┘
                 │
                 ▼
        ┌─────────────────┐
        │   Raspberry Pi  │
        │   WOL サービス  │
        │  （ポート 5000）│
        │                 │
        │ - Flask Web UI  │
        │ - REST API      │
        │ - WOL パケット  │
        └────────┬────────┘
                 │
        ┌────────┴──────────┐
        │ ブロードキャスト  │
        │ ネットワーク      │
        │ （UDP マルチ）    │
        │ （IP: 255.255...）│
        └────────┬──────────┘
                 │
                 ▼
        ┌─────────────────┐
        │    PC システム  │
        │                 │
        │ 電源制御        │
        │ API (5001)      │
        │                 │
        │ - 状態確認      │
        │ - シャットダウン│
        │ - 電源状態      │
        └─────────────────┘
```

**コンポーネント**:
- **Raspberry Pi WOL サービス**: Raspberry Pi で動作、Flask Web UI と REST API で電源制御を提供
- **PC 電源 API**: 対象 PC で動作、システム電源状態を制御・ヘルスチェック提供
- **Docker レジストリ**: `ghcr.io/shiomi680/power-on-rpi` と `ghcr.io/shiomi680/power-on-pc` にイメージ保存

**通信フロー**:
1. ユーザーが Web UI または API でコマンド送信（Raspberry Pi、ポート 5000）
2. Raspberry Pi が WOL マジックパケットまたは HTTP API 呼び出しを生成
3. PC がスリープから復帰または電源コマンド実行
4. 状態が Web UI または API レスポンスでユーザーに返される

---

## デプロイメントガイド

### Raspberry Pi WOL サービス

**所要時間**: 10～15 分  
**難易度**: 初級  
**対象**: Raspberry Pi 3B+ 以上（4GB RAM 推奨）

#### ステップ 1: リポジトリのクローン

```bash
# Raspberry Pi に SSH 接続
ssh pi@<rpi-ip-address>

# リポジトリのクローン
git clone https://github.com/shiomi680/power-on.git
cd power-on
```

**期待される出力**:
```
Cloning into 'power-on'...
remote: Enumerating objects...
[進捗メッセージ]
done.
```

#### ステップ 2: 環境変数の設定

PC の詳細情報で `.env` ファイルを編集：

```bash
# 環境テンプレートをコピー
cp rpi-wol/.env.example rpi-wol/.env

# PC 情報を編集
nano rpi-wol/.env
```

**これらの値を設定**:

| 変数 | 例 | 説明 |
|------|-----|------|
| `PC_ADDRESS` | `192.168.1.100` | ネットワーク上の PC の IP アドレス |
| `PC_API_PORT` | `5001` | PC API がリッスンするポート |
| `PC_API_TIMEOUT` | `5` | PC API 呼び出しのタイムアウト（秒） |
| `WOL_TARGET_MAC` | `aa:bb:cc:dd:ee:ff` | 対象 PC の MAC アドレス |
| `WOL_BROADCAST_IP` | `255.255.255.255` | WOL パケットのブロードキャストアドレス |
| `LOG_LEVEL` | `INFO` | ログレベル（DEBUG, INFO, WARNING, ERROR） |

**PC の MAC アドレスを確認する方法**:

- **Linux**: `ip addr show`（`link/ether` エントリを探す）
- **macOS**: `ifconfig`（`ether` エントリを探す）
- **Windows**: `ipconfig /all`（`物理アドレス` を探す）

#### ステップ 3: サービスの起動

```bash
# Raspberry Pi WOL サービスを起動
cd power-on/rpi-wol
docker compose up -d
```

**期待される出力**:
```
[+] Running 2/2
 ✔ Container power-on-rpi-web-1      Started
 ✔ Container power-on-rpi-redis-1     Started
```

#### ステップ 4: サービス稼働確認

```bash
# コンテナ状態を確認
docker compose ps

# ヘルスエンドポイントをテスト
curl http://localhost:5000/health
```

**期待されるヘルスチェック応答**:
```json
{
  "status": "ok",
  "service": "rpi-wol",
  "timestamp": "2026-04-29T10:00:00Z"
}
```

#### ステップ 5: Web UI にアクセス

ブラウザで開く: `http://<rpi-ip-address>:5000`

PC の電源状態を制御するボタンが表示されたダッシュボードが見えます。

---

### PC 電源制御 API

**所要時間**: 5～10 分  
**難易度**: 初級  
**対象**: Windows、Linux、macOS PC

#### ステップ 1: リポジトリのクローン

```bash
# 制御対象の PC 上で実行
git clone https://github.com/shiomi680/power-on.git
cd power-on
```

#### ステップ 2: 環境変数の設定

```bash
# 環境テンプレートをコピー
cp pc-power/.env.example pc-power/.env

# 設定を編集（必要に応じて SHUTDOWN_TIMEOUT を調整）
# nano pc-power/.env    (Linux/macOS)
# notepad pc-power\.env (Windows PowerShell)
```

**これらの値を設定**:

| 変数 | デフォルト | 説明 |
|------|-----------|------|
| `SHUTDOWN_TIMEOUT` | `60` | シャットダウン前の待機時間（秒）（保存・クリーンアップ用） |
| `LOG_LEVEL` | `INFO` | ログレベル（DEBUG, INFO, WARNING, ERROR） |

#### ステップ 3: サービスの起動

```bash
# Linux/macOS
cd power-on/pc-power
docker compose up -d

# または Python で手動実行
cd power-on/pc-power
pip install -r requirements.txt
python -m src.flask_app
```

**期待される出力**:
```
[+] Running 1/1
 ✔ Container power-on-pc-api-1       Started
```

#### ステップ 4: API 稼働確認

```bash
# ヘルスエンドポイントを確認
curl http://localhost:5001/health
```

**期待される応答**:
```json
{
  "status": "ok",
  "service": "pc-power",
  "timestamp": "2026-04-29T10:00:00Z"
}
```

#### ステップ 5: 電源制御 API をテスト

```bash
# 現在の電源状態を取得
curl http://localhost:5001/api/power/status

# 応答例
{"state": "on", "uptime_seconds": 3600}
```

---

### Docker デプロイメント（両サービス）

**所要時間**: 2～3 分  
**難易度**: 初級  
**推奨**: 最も簡単なデプロイ方法

#### Docker Compose でクイックスタート

リポジトリルートから実行：

```bash
# 環境テンプレートをコピー
cp rpi-wol/.env.example rpi-wol/.env
cp pc-power/.env.example pc-power/.env

# PC_ADDRESS と MAC アドレスを設定
nano rpi-wol/.env

# 両サービスを起動
docker compose up -d
```

#### 両サービスの確認

```bash
# 実行中のコンテナを列表示
docker compose ps

# Raspberry Pi サービス（WOL）をテスト
curl http://localhost:5000/health

# PC サービス（電源 API）をテスト
curl http://localhost:5001/health
```

**期待される出力**:
```
NAME                     COMMAND                  SERVICE      STATUS
power-on-rpi-web        python -m src.flask_app  rpi-wol      Up 2 minutes
power-on-rpi-redis      redis-server             rpi-wol      Up 2 minutes
power-on-pc-api         python -m src.flask_app  pc-power     Up 2 minutes
```

#### 事前ビルドイメージの取得

GitHub Container Registry へのアクセスがある場合：

```bash
# ghcr.io からイメージを取得
docker pull ghcr.io/shiomi680/power-on-rpi:latest
docker pull ghcr.io/shiomi680/power-on-pc:latest

# docker-compose.yml で参照:
# image: ghcr.io/shiomi680/power-on-rpi:latest
```

---

## 環境変数

すべての設定オプションの完全リファレンス。

### Raspberry Pi WOL サービス（`rpi-wol/.env`）

| 変数 | 必須 | デフォルト | 例 | 説明 |
|------|------|---------|------|------|
| `PC_ADDRESS` | ✅ Yes | - | `192.168.1.100` | 対象 PC の IP アドレスまたはホスト名 |
| `PC_API_PORT` | ✅ Yes | - | `5001` | PC API がリッスンするポート |
| `PC_API_TIMEOUT` | ❌ No | `5` | `10` | API タイムアウト（秒） |
| `WOL_TARGET_MAC` | ✅ Yes | - | `aa:bb:cc:dd:ee:ff` | 対象 PC の MAC アドレス |
| `WOL_BROADCAST_IP` | ❌ No | `255.255.255.255` | `192.168.1.255` | WOL パケットのブロードキャストアドレス |
| `FLASK_HOST` | ❌ No | `0.0.0.0` | `localhost` | Flask サーバーバインドアドレス |
| `FLASK_PORT` | ❌ No | `5000` | `5000` | Flask サーバーポート |
| `LOG_LEVEL` | ❌ No | `INFO` | `DEBUG` | ログレベル（DEBUG, INFO, WARNING, ERROR） |

### PC 電源制御 API（`pc-power/.env`）

| 変数 | 必須 | デフォルト | 例 | 説明 |
|------|------|---------|------|------|
| `SHUTDOWN_TIMEOUT` | ❌ No | `60` | `120` | シャットダウン前の待機時間（秒） |
| `FLASK_HOST` | ❌ No | `0.0.0.0` | `localhost` | Flask サーバーバインドアドレス |
| `FLASK_PORT` | ❌ No | `5001` | `5001` | Flask サーバーポート |
| `LOG_LEVEL` | ❌ No | `INFO` | `DEBUG` | ログレベル（DEBUG, INFO, WARNING, ERROR） |

### テンプレートファイル

提供されているテンプレートから始めます：

```bash
# Raspberry Pi テンプレート
cat rpi-wol/.env.example

# PC テンプレート
cat pc-power/.env.example
```

---

## トラブルシューティング

### 一般的な問題と解決方法

#### ポート 5000 または 5001 が既に使用中

**症状**: `Address already in use` または `bind: permission denied`

**解決方法**:
```bash
# ポート使用中のプロセスを確認（Linux/macOS）
lsof -i :5000
lsof -i :5001

# プロセスを終了（PID を置換）
kill -9 <PID>

# または docker-compose.yml でポートを変更
# 編集: ports: - "8000:5000"  （ポート 8000 を代わりに使用）
```

#### Raspberry Pi から PC に接続できない

**症状**: Web UI は動作するが、電源制御コマンドは失敗

**診断**:
```bash
# PC へのネットワーク接続確認
ping <PC_ADDRESS>

# API を直接テスト
curl http://<PC_ADDRESS>:5001/health

# PC のファイアウォール確認
# - Windows: Windows Defender でポート 5001 を許可
# - Linux: iptables/ufw ルールを確認
```

**解決方法**:
- `.env` の `PC_ADDRESS` が正確か確認（最初はホスト名ではなく IP を使用）
- 両デバイスが同じ LAN/サブネット上か確認
- PC のファイアウォール設定を確認
- PC 電源 API が動作中か確認: `curl http://localhost:5001/health`

#### Docker コンテナが直ちに終了

**症状**: `docker compose ps` で「Exited」と表示

**診断**:
```bash
# コンテナログを確認
docker compose logs rpi-wol

# または特定のコンテナ
docker logs power-on-rpi-web-1
```

**解決方法**:
- ログで Python インポートエラーを確認
- `.env` ファイルが存在・読み取り可能か確認
- すべての必須環境変数が設定されているか確認
- Docker デーモンが実行中か確認: `docker ps`

#### WOL マジックパケットが受信されない

**症状**: WOL コマンド送信時に PC が起動しない

**診断**:
```bash
# MAC アドレスが正確か確認
ip addr show         # （PC 上で）

# WOL をローカルテスト（Raspberry Pi 上）
arp-scan -l          # ネットワーク上で PC の MAC を確認
```

**解決方法**:
- `.env` の MAC アドレスを確認（`ip addr` または `ipconfig /all` で取得）
- BIOS を確認: PC で Wake-On-LAN を有効化必須
- Raspberry Pi がブロードキャストアドレスに到達可能か確認: `ping 255.255.255.255`
- ブロードキャストを絞る: `WOL_BROADCAST_IP` をサブネットブロードキャストに設定（例: `192.168.1.255`）

#### パーミッション拒否エラー

**症状**: `Permission denied` または `Operation not permitted`

**解決方法**（Linux/Raspberry Pi）:
```bash
# 現在のユーザーが Docker にアクセス可能にする
sudo usermod -aG docker $USER
newgrp docker

# または sudo で実行
sudo docker compose up -d
```

#### CPU 使用率が高い またはメモリ不足

**症状**: システムが遅くなる、プロセスが強制終了される

**解決方法**:
```bash
# リソース使用状況を確認
docker stats

# 低メモリシステム（Pi Zero）の場合、docker-compose.yml を編集:
# 追加: deploy:
#        resources:
#          limits:
#            memory: 256M
```

#### 接続タイムアウト またはネットワーク問題

**症状**: `Connection refused`、`Network is unreachable`、またはタイムアウト

**診断**:
```bash
# Raspberry Pi から PC への接続をテスト
nc -zv <PC_ADDRESS> 5001    # netcat テスト
curl -v http://<PC_ADDRESS>:5001/health

# ネットワークルーティングを確認
ip route
```

**解決方法**:
- 両デバイスが同じサブネット上か確認（両方向で `ping` を使用）
- ルーター・ネットワーク設定を確認
- 遅いネットワークの場合、`.env` の `PC_API_TIMEOUT` を増加
- トラフィックをブロックするネットワーク ACL がないか確認

#### Redis 接続エラー

**症状**: Redis サービスが起動失敗（Docker ログでエラー表示）

**解決方法**:
```bash
# Redis は rpi-wol のキャッシング用
# Docker に十分なディスク容量があるか確認
docker system df

# 不要なイメージをクリア（必要に応じて）
docker system prune
```

### サポート受付

1. まずログを確認：
   ```bash
   docker compose logs --tail 50
   ```

2. すべての .env 変数を確認：
   ```bash
   cat rpi-wol/.env
   ```

3. エンドポイントを手動テスト：
   ```bash
   curl http://localhost:5000/health
   curl http://localhost:5001/health
   ```

4. ネットワーク設定を確認：
   ```bash
   ifconfig              # (Linux/macOS)
   ipconfig              # (Windows)
   ping <target-ip>
   arp-scan -l           # (Linux/macOS)
   ```

---

## バージョン管理と ghcr.io 自動ビルド・プッシュ

### Git Tag で ghcr.io イメージをビルド・プッシュ

`v*` パターンで git tag を作成すると、GitHub Actions が自動的にイメージをビルドして ghcr.io にプッシュします。

#### ステップ 1: バージョンタグを作成

```bash
# version.json でバージョン情報を管理（参考用）
cat version.json
# { "version": "1.0.0", ... }

# git tag を作成（v で始まる tag が対象）
git tag v1.0.0

# タグをプッシュ
git push origin v1.0.0
```

#### ステップ 2: GitHub Actions が自動実行

tag push すると、GitHub Actions が以下を実行：
1. イメージをビルド
2. ghcr.io に以下のタグでプッシュ：
   - `ghcr.io/shiomi680/power-on/power-on-rpi:1.0.0`
   - `ghcr.io/shiomi680/power-on/power-on-pc:1.0.0`
   - `ghcr.io/shiomi680/power-on/power-on-rpi:1` (major.minor)
   - `ghcr.io/shiomi680/power-on/power-on-rpi:sha-<commit>` (SHA)

**所要時間**: 2-5 分

#### ステップ 3: イメージを確認

```bash
# ビルド完了後、イメージを確認
docker pull ghcr.io/shiomi680/power-on/power-on-rpi:1.0.0

# タグを確認
docker inspect ghcr.io/shiomi680/power-on/power-on-rpi:1.0.0 | grep RepoTags
```

#### docker-compose.yml でバージョンを指定

```yaml
services:
  rpi-wol:
    image: ghcr.io/shiomi680/power-on-rpi:1.0.0
  pc-power:
    image: ghcr.io/shiomi680/power-on-pc:1.0.0
```

#### バージョンアップ手順

```bash
# 1. バージョン情報を更新（参考用）
nano version.json
# "version": "1.0.0" → "1.1.0"

# 2. コミット
git add version.json
git commit -m "chore: version bump to 1.1.0"
git push origin main

# 3. タグを作成・プッシュ
git tag v1.1.0
git push origin v1.1.0

# 4. GitHub Actions が自動実行（2-5分）
# → ghcr.io:1.1.0 でイメージをビルド・プッシュ
```

---

## 関連ドキュメント

詳細については以下を参照してください：

- **[Docker デプロイメント](docs/DOCKER.md)** - Docker イメージ、レジストリ、ヘルスチェック
- **[デプロイメントガイド](docs/DEPLOYMENT.md)** - ハードウェア上の本番環境デプロイメント
- **[CI/CD パイプライン](docs/CI-CD.md)** - GitHub Actions、自動テスト、イメージビルド
- **[アーキテクチャ](docs/ARCHITECTURE.md)** - システム設計とコンポーネント詳細

---

## 開発

### 開発環境の前提条件

```bash
# リポジトリのクローン
git clone https://github.com/shiomi680/power-on.git
cd power-on

# 仮想環境を作成
python -m venv venv
source venv/bin/activate  # (Linux/macOS)
# または
py -m venv venv && venv\Scripts\activate  # (Windows)

# 依存関係をインストール
pip install -r rpi-wol/requirements.txt
pip install -r pc-power/requirements.txt

# テストを実行
pytest rpi-wol/tests/
pytest pc-power/tests/
```

### Docker なしでローカル実行

```bash
# ターミナル 1: Raspberry Pi WOL サービス
cd rpi-wol
export FLASK_PORT=5000
python -m src.flask_app

# ターミナル 2: PC 電源 API
cd pc-power
export FLASK_PORT=5001
python -m src.flask_app
```

---

## 貢献

1. リポジトリをフォーク
2. フィーチャーブランチを作成: `git checkout -b feature/your-feature`
3. 変更をコミット: `git commit -am 'Add feature'`
4. ブランチにプッシュ: `git push origin feature/your-feature`
5. プルリクエストを送信

すべての貢献はテストとドキュメントを含める必要があります。

---

## ライセンス

MIT ライセンス - LICENSE ファイルを参照してください

---

**最終更新**: 2026-04-29  
**保守者**: Genki Team  
**Issues**: [GitHub Issues](https://github.com/shiomi680/power-on/issues)
