# API リクエスト/レスポンス スキーマ定義

SHUTDOWN_REQUEST = {
    "type": "object",
    "properties": {
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
            "enum": ["online"],
            "description": "PC は常にオンライン（起動状態）"
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
