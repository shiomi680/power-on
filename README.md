# Power-On: リモート PC 電源制御システム

[![GitHub Actions: CI/CD](https://github.com/shiomi680/power-on/actions/workflows/docker-publish.yml/badge.svg)](https://github.com/shiomi680/power-on/actions)
[![Container Registry](https://img.shields.io/badge/registry-ghcr.io-blue)](https://github.com/shiomi680/power-on/pkgs/container/)

Raspberry Pi から PC の電源状態を制御する Wake-on-LAN（WOL）・電源管理システム。Docker によるマルチプラットフォーム対応でデプロイ可能。

## 目次

- [クイックスタート（5 分）](#クイックスタート)
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

## クイックスタート

Docker Compose ワンコマンドで両サービスをデプロイ：

```bash
# リポジトリのクローン
git clone https://github.com/shiomi680/power-on.git
cd power-on

# 環境テンプレートをコピーして設定（環境変数セクション参照）
# 基本テストの場合は docker-compose.yml のデフォルト値を使用可

# 両サービスを起動
docker compose up -d

# サービスが実行中か確認
curl http://localhost:5000/health     # Raspberry Pi WOL サービス
curl http://localhost:5001/health     # PC 電源制御 API
```

**期待される出力**:
- Raspberry Pi Web UI: http://localhost:5000（動作中）
- PC API ヘルスチェック: `{"status": "ok"}` を返す（ポート 5001）

両サービスは 2 分以内に起動します。

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
