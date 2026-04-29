"""
Raspberry Pi WOL CLI インターフェース

使用法:
  python -m cli send-wol --mac xx:xx:xx:xx:xx:xx
  python -m cli run-server --port 5000
"""

import argparse
import sys
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from wol_service import WOLService
from flask_app import app
from config import FLASK_PORT, FLASK_HOST


def setup_logging(verbose=False):
    """ロギング設定"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def cmd_send_wol(args):
    """WOL パケット送信コマンド"""
    try:
        service = WOLService()
        result = service.send(args.mac)

        if args.json:
            print(json.dumps(result))
        else:
            print(f"✓ WOL パケットを送信しました")
            print(f"  ターゲット MAC: {args.mac}")
            print(f"  タイムスタンプ: {result['timestamp']}")

        return 0

    except ValueError as e:
        if args.json:
            print(json.dumps({"error": str(e), "code": "invalid_mac"}))
        else:
            print(f"✗ エラー: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "code": "send_failed"}))
        else:
            print(f"✗ エラー: WOL パケット送信に失敗しました: {e}", file=sys.stderr)
        return 1


def cmd_run_server(args):
    """Flask サーバー起動コマンド"""
    try:
        port = args.port or FLASK_PORT
        host = args.host or FLASK_HOST

        if args.json:
            print(json.dumps({
                "status": "server_starting",
                "host": host,
                "port": port
            }))

        print(f"Flask サーバーを起動しています...")
        print(f"  アドレス: http://{host}:{port}")
        print(f"  Press CTRL+C to stop")

        app.run(host=host, port=port, debug=args.debug)
        return 0

    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "code": "server_failed"}))
        else:
            print(f"✗ エラー: サーバー起動に失敗しました: {e}", file=sys.stderr)
        return 1


def main():
    """メインエントリーポイント"""
    parser = argparse.ArgumentParser(
        description="Raspberry Pi WOL サービス CLI",
        prog="power-on-rpi"
    )

    # グローバルオプション
    parser.add_argument("--json", action="store_true", help="JSON 形式で出力")
    parser.add_argument("-v", "--verbose", action="store_true", help="詳細出力")

    # サブコマンド
    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # send-wol コマンド
    send_wol_parser = subparsers.add_parser(
        "send-wol",
        help="WOL パケットを送信"
    )
    send_wol_parser.add_argument(
        "--mac",
        required=True,
        help="ターゲット PC の MAC アドレス (xx:xx:xx:xx:xx:xx)"
    )
    send_wol_parser.set_defaults(func=cmd_send_wol)

    # run-server コマンド
    run_server_parser = subparsers.add_parser(
        "run-server",
        help="Flask サーバーを起動"
    )
    run_server_parser.add_argument(
        "--port",
        type=int,
        help="サーバーポート (デフォルト: 5000)"
    )
    run_server_parser.add_argument(
        "--host",
        default="0.0.0.0",
        help="バインドホスト (デフォルト: 0.0.0.0)"
    )
    run_server_parser.add_argument(
        "--debug",
        action="store_true",
        help="デバッグモード"
    )
    run_server_parser.set_defaults(func=cmd_run_server)

    # パース
    args = parser.parse_args()
    setup_logging(args.verbose)

    # コマンド実行
    if not args.command:
        parser.print_help()
        return 0

    return args.func(args)


if __name__ == "__main__":
    sys.exit(main())
