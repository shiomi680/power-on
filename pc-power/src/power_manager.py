# PC 電源管理コアライブラリ

import subprocess
import logging
from config import get_timestamp, SHUTDOWN_TIMEOUT, SHUTDOWN_COMMAND

logger = logging.getLogger(__name__)

class PowerManager:
    """PC 電源管理サービス"""

    def __init__(self, timeout=SHUTDOWN_TIMEOUT):
        """初期化

        Args:
            timeout: シャットダウンタイムアウト（秒）
        """
        self.timeout = timeout
        self.shutdown_in_progress = False

    def shutdown(self, timeout=None):
        """PC をシャットダウン

        Args:
            timeout: シャットダウンタイムアウト（秒）。None なら self.timeout を使用

        Returns:
            dict: 実行結果 {"status": "shutdown_initiated", "timestamp": "..."}

        Raises:
            RuntimeError: シャットダウンコマンド実行失敗またはシャットダウン既進行中
        """
        if self.shutdown_in_progress:
            raise RuntimeError("Shutdown already in progress")

        if timeout is None:
            timeout = self.timeout

        try:
            self.shutdown_in_progress = True

            # Linux シャットダウンコマンド
            # `shutdown -h +1` で 1 分後にシャットダウン
            cmd = f"shutdown -h +{max(1, timeout // 60)}"

            logger.info(f"Executing shutdown command: {cmd}")
            subprocess.run(cmd, shell=True, check=True, capture_output=True, timeout=2)

            return {
                "status": "shutdown_initiated",
                "timestamp": get_timestamp()
            }

        except subprocess.TimeoutExpired:
            logger.warning(f"Shutdown command timed out after 2s (may still be scheduled)")
            return {
                "status": "shutdown_initiated",
                "timestamp": get_timestamp()
            }
        except subprocess.CalledProcessError as e:
            logger.error(f"Failed to execute shutdown command: {e}")
            self.shutdown_in_progress = False
            raise RuntimeError(f"Shutdown command failed: {e}")
        except Exception as e:
            logger.error(f"Unexpected error during shutdown: {e}")
            self.shutdown_in_progress = False
            raise

    def get_status(self):
        """PC の状態を取得

        Returns:
            dict: ステータス {"status": "online", "timestamp": "..."}
        """
        # このサーバーが起動していれば、PC は online
        return {
            "status": "online",
            "timestamp": get_timestamp()
        }

    def cancel_shutdown(self):
        """シャットダウンをキャンセル

        Returns:
            dict: 実行結果
        """
        try:
            cmd = "shutdown -c"
            logger.info("Canceling shutdown")
            subprocess.run(cmd, shell=True, check=True, capture_output=True)
            self.shutdown_in_progress = False

            return {
                "status": "shutdown_canceled",
                "timestamp": get_timestamp()
            }
        except Exception as e:
            logger.error(f"Failed to cancel shutdown: {e}")
            raise RuntimeError(f"Failed to cancel shutdown: {e}")
