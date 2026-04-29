# Power On システム デプロイメントガイド

PC と Raspberry Pi を別のハードウェアにデプロイする手順。

## システムアーキテクチャ

```
┌─────────────────────────────┐
│   Raspberry Pi (192.168.1.10) │
│  ┌────────────────────────┐ │
│  │   Docker Container     │ │
│  │  - Flask Web UI :5000  │ │
│  │  - WOL Service         │ │
│  │  - PC Proxy API        │ │
│  └────────────────────────┘ │
└──────────────┬──────────────┘
               │ HTTP :5001
               ▼
┌─────────────────────────────┐
│   PC (192.168.1.100)       │
│  ┌────────────────────────┐ │
│  │   Docker Container     │ │
│  │  - Flask API :5001     │ │
│  │  - Shutdown Manager    │ │
│  │  - Status Service      │ │
│  └────────────────────────┘ │
└─────────────────────────────┘

┌─────────────────────────────┐
│   User Browser              │
│  - Any Device on Network    │
│  - http://rpi-ip:5000       │
└──────────────┬──────────────┘
               │
               ▼ Web UI
        Raspberry Pi
```

## デプロイメント手順

### Raspberry Pi へのデプロイ

#### 1. Raspberry Pi に SSH でログイン

```bash
ssh pi@your-rpi-ip
```

#### 2. リポジトリをクローン

```bash
cd ~
git clone https://github.com/your-repo/power-on.git
cd power-on/rpi-wol
```

#### 3. 環境設定

```bash
# テンプレートをコピー
cp .env.example .env

# PC のアドレスを設定
nano .env
```

設定内容:

```bash
# PC のアドレス（重要！）
PC_ADDRESS=192.168.1.100

# ターゲット PC の MAC アドレス
WOL_TARGET_MAC=aa:bb:cc:dd:ee:ff
```

#### 4. デプロイ

```bash
docker compose up -d
```

#### 5. 確認

```bash
# ヘルスチェック
curl http://localhost:5000/api/health

# ブラウザから確認
# http://your-rpi-ip:5000
```

---

### PC へのデプロイ

#### 1. PC に SSH でログイン（Linux）

```bash
ssh user@your-pc-ip
# または localhost
```

#### 2. リポジトリをクローン

```bash
cd ~
git clone https://github.com/your-repo/power-on.git
cd power-on/pc-power
```

#### 3. 環境設定

```bash
# テンプレートをコピー
cp .env.example .env

# 必要に応じて編集（デフォルトで動作）
nano .env
```

#### 4. デプロイ

```bash
docker compose up -d
```

#### 5. 確認

```bash
# ヘルスチェック
curl http://localhost:5001/api/health

# ステータス確認
curl http://localhost:5001/api/power/status
```

---

## ネットワーク確認

### Raspberry Pi から PC への接続確認

```bash
# Raspberry Pi コンテナから PC にアクセス可能か確認
docker compose exec rpi-wol curl http://192.168.1.100:5001/api/health
```

### PC のアドレスを確認

```bash
# PC のローカルネットワーク IP を確認
ifconfig | grep -A1 "eth0\|wlan0"
# または
hostname -I
```

---

## 設定ファイル一覧

### Raspberry Pi

```
rpi-wol/
├── docker-compose.yml    # Raspberry Pi 用 Compose
├── .env                  # 環境変数（PC_ADDRESS などを設定）
├── .env.example          # テンプレート
├── Dockerfile            # イメージ定義
└── DEPLOY.md             # 詳細ガイド
```

### PC

```
pc-power/
├── docker-compose.yml    # PC 用 Compose
├── .env                  # 環境変数（オプション）
├── .env.example          # テンプレート
├── Dockerfile            # イメージ定義
└── DEPLOY.md             # 詳細ガイド
```

---

## よく使うコマンド

### Raspberry Pi での操作

```bash
cd ~/power-on/rpi-wol

# ログ確認
docker compose logs -f

# 停止
docker compose down

# 再起動
docker compose restart

# コンテナ状態
docker compose ps
```

### PC での操作

```bash
cd ~/power-on/pc-power

# ログ確認
docker compose logs -f

# 停止
docker compose down

# 再起動
docker compose restart

# コンテナ状態
docker compose ps
```

---

## トラブルシューティング

### Raspberry Pi から PC に接続できない

```bash
# PC のアドレスを確認
ping 192.168.1.100

# PC のファイアウォール設定を確認
sudo ufw status

# ポート 5001 を許可（PC）
sudo ufw allow 5001
```

### Web UI が表示されない

```bash
# Raspberry Pi のポート確認
netstat -tuln | grep 5000

# コンテナログ確認
docker compose logs rpi-wol
```

### WOL が動作しない

```bash
# Raspberry Pi から WOL テスト
docker compose exec rpi-wol python -m cli send-wol --mac aa:bb:cc:dd:ee:ff

# PC の BIOS で WOL を有効化していることを確認
# PC の MAC アドレスが正しいことを確認
```

---

## 開発環境での動作確認

### ローカルで全体をテスト（開発用）

```bash
# プロジェクトルートで
docker compose up -d

# http://localhost:5000 にアクセス
```

個別の docker-compose.yml を使用せず、ルートの docker-compose.yml を使用してローカルテストします。

---

## セキュリティに関する注意

### ファイアウォール設定

```bash
# Raspberry Pi（Web UI）
sudo ufw allow 5000

# PC（API）
sudo ufw allow 5001
```

### HTTPS/SSL の設定（本番環境）

nginx などのリバースプロキシで HTTPS 化を推奨。

### 認証の追加（本番環境）

現在は認証がないため、LAN 内のみアクセス可能にしてください。

---

## 自動起動設定

### Raspberry Pi で自動起動

```bash
# systemd サービス作成
sudo nano /etc/systemd/system/power-on-rpi.service
```

詳細は `rpi-wol/DEPLOY.md` を参照。

### PC で自動起動

```bash
# systemd サービス作成
sudo nano /etc/systemd/system/power-on-pc.service
```

詳細は `pc-power/DEPLOY.md` を参照。

---

## 詳細ガイド

各コンポーネントの詳細は専用ガイドを参照:

- **Raspberry Pi**: `rpi-wol/DEPLOY.md`
- **PC**: `pc-power/DEPLOY.md`
- **Docker**: `docs/DOCKER.md`

---

## サポートされているプラットフォーム

| プラットフォーム | Raspberry Pi | PC |
|------------------|-------------|-----|
| Linux | ✅ | ✅ |
| macOS | ✅ (テスト用) | ✅ |
| Windows | ⚠️ WSL2 | ⚠️ WSL2 |

Windows では WSL2 + Docker Desktop を推奨。
