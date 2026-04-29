"""
PC 電源管理 CLI インターフェース

使用法:
  python -m cli shutdown --timeout 60
  python -m cli status
  python -m cli run-server --port 5001
"""

import argparse
import sys
import json
import logging
from pathlib import Path

# Add src to path
sys.path.insert(0, str(Path(__file__).parent))

from power_manager import PowerManager
from flask_app import app
from config import FLASK_PORT, FLASK_HOST


def setup_logging(verbose=False):
    """ロギング設定"""
    level = logging.DEBUG if verbose else logging.INFO
    logging.basicConfig(
        level=level,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )


def cmd_shutdown(args):
    """シャットダウンコマンド"""
    try:
        manager = PowerManager()
        result = manager.shutdown(args.timeout)

        if args.json:
            print(json.dumps(result))
        else:
            print(f"✓ シャットダウンを開始しました")
            print(f"  タイムアウト: {args.timeout} 秒")
            print(f"  タイムスタンプ: {result['timestamp']}")

        return 0

    except RuntimeError as e:
        if args.json:
            print(json.dumps({"error": str(e), "code": "shutdown_failed"}))
        else:
            print(f"✗ エラー: {e}", file=sys.stderr)
        return 1

    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "code": "shutdown_failed"}))
        else:
            print(f"✗ エラー: シャットダウンに失敗しました: {e}", file=sys.stderr)
        return 1


def cmd_status(args):
    """ステータス確認コマンド"""
    try:
        manager = PowerManager()
        result = manager.get_status()

        if args.json:
            print(json.dumps(result))
        else:
            status_text = {
                "online": "オンライン",
                "offline": "オフライン",
                "unknown": "不明"
            }
            print(f"✓ PC の状態: {status_text.get(result['status'], result['status'])}")
            print(f"  タイムスタンプ: {result['timestamp']}")

        return 0

    except Exception as e:
        if args.json:
            print(json.dumps({"error": str(e), "code": "status_failed"}))
        else:
            print(f"✗ エラー: ステータス確認に失敗しました: {e}", file=sys.stderr)
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
        description="PC 電源管理 CLI",
        prog="power-on-pc"
    )

    # グローバルオプション
    parser.add_argument("--json", action="store_true", help="JSON 形式で出力")
    parser.add_argument("-v", "--verbose", action="store_true", help="詳細出力")

    # サブコマンド
    subparsers = parser.add_subparsers(dest="command", help="コマンド")

    # shutdown コマンド
    shutdown_parser = subparsers.add_parser(
        "shutdown",
        help="PC をシャットダウン"
    )
    shutdown_parser.add_argument(
        "--timeout",
        type=int,
        default=60,
        help="シャットダウンタイムアウト（秒、デフォルト: 60）"
    )
    shutdown_parser.set_defaults(func=cmd_shutdown)

    # status コマンド
    status_parser = subparsers.add_parser(
        "status",
        help="PC の状態確認"
    )
    status_parser.set_defaults(func=cmd_status)

    # run-server コマンド
    run_server_parser = subparsers.add_parser(
        "run-server",
        help="Flask サーバーを起動"
    )
    run_server_parser.add_argument(
        "--port",
        type=int,
        default=5001,
        help="サーバーポート (デフォルト: 5001)"
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
