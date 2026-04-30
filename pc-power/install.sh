#!/bin/bash
# PC 電源管理サービス インストールスクリプト

set -e

echo "========================================="
echo "PC 電源管理サービス (pc-power) インストール"
echo "========================================="

# 権限確認
if [[ $EUID -ne 0 ]]; then
   echo "このスクリプトは root 権限で実行してください"
   echo "実行: sudo bash install.sh"
   exit 1
fi

# ディレクトリ準備
echo "[1/5] ディレクトリ準備中..."
mkdir -p /opt/pc-power
cp -r . /opt/pc-power/
cd /opt/pc-power
chmod 755 /opt/pc-power

# Python パッケージインストール
echo "[2/5] Python パッケージインストール中..."
pip install -e /opt/pc-power

# 環境変数ファイル設定
echo "[3/5] 環境変数ファイル設定中..."
if [ ! -f /opt/pc-power/.env ]; then
    cp .env.example .env
    chmod 600 /opt/pc-power/.env
    echo "  → .env を作成しました。必要に応じて編集してください:"
    echo "     nano /opt/pc-power/.env"
fi

# systemd service インストール
echo "[4/5] systemd service インストール中..."
cp /opt/pc-power/pc-power.service /etc/systemd/system/
chmod 644 /etc/systemd/system/pc-power.service
systemctl daemon-reload
systemctl enable pc-power

# サービス起動
echo "[5/5] サービス起動中..."
systemctl start pc-power

# 確認
echo ""
echo "========================================="
echo "インストール完了！"
echo "========================================="
echo ""
echo "ステータス確認:"
echo "  systemctl status pc-power"
echo ""
echo "ログ確認:"
echo "  journalctl -u pc-power -f"
echo ""
echo "API テスト:"
echo "  curl http://localhost:5001/api/health"
echo "  curl http://localhost:5001/api/power/status"
