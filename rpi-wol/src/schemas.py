# API リクエスト/レスポンス スキーマ定義

POWER_ON_REQUEST = {
    "type": "object",
    "required": ["target_mac"],
    "properties": {
        "target_mac": {
            "type": "string",
            "pattern": "^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$",
            "description": "ターゲット PC の MAC アドレス (xx:xx:xx:xx:xx:xx)"
        }
    }
}

POWER_SHUTDOWN_REQUEST = {
    "type": "object",
    "required": ["pc_address"],
    "properties": {
        "pc_address": {
            "type": "string",
            "description": "ターゲット PC の IP アドレス"
        },
        "timeout": {
            "type": "integer",
            "default": 60,
            "description": "シャットダウンタイムアウト（秒）"
        }
    }
}

STATUS_RESPONSE = {
    "type": "object",
    "required": ["status", "timestamp"],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["online", "offline", "unknown"],
            "description": "PC の電源状態"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO8601 タイムスタンプ"
        }
    }
}

POWER_ON_RESPONSE = {
    "type": "object",
    "required": ["status", "timestamp"],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["packet_sent"],
            "description": "WOL パケット送信完了"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO8601 タイムスタンプ"
        }
    }
}

SHUTDOWN_RESPONSE = {
    "type": "object",
    "required": ["status", "timestamp"],
    "properties": {
        "status": {
            "type": "string",
            "enum": ["shutdown_initiated"],
            "description": "シャットダウン開始"
        },
        "timestamp": {
            "type": "string",
            "format": "date-time",
            "description": "ISO8601 タイムスタンプ"
        }
    }
}

ERROR_RESPONSE = {
    "type": "object",
    "required": ["error", "code"],
    "properties": {
        "error": {
            "type": "string",
            "description": "エラーメッセージ"
        },
        "code": {
            "type": "string",
            "description": "エラーコード"
        }
    }
}
