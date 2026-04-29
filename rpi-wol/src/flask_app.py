from flask import Flask, render_template, jsonify, request
from config import FLASK_PORT, FLASK_HOST, FLASK_DEBUG, get_timestamp
import logging

# ロギング設定
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__,
            template_folder="../templates",
            static_folder="../static")

@app.route("/", methods=["GET"])
def index():
    """Web UI メインページ"""
    return render_template("index.html")

@app.route("/api/health", methods=["GET"])
def health():
    """ヘルスチェックエンドポイント"""
    return jsonify({
        "status": "ok",
        "timestamp": get_timestamp()
    })

@app.errorhandler(400)
def bad_request(e):
    """400 Bad Request ハンドラ"""
    return jsonify({
        "error": "リクエストが無効です",
        "code": "bad_request"
    }), 400

@app.errorhandler(404)
def not_found(e):
    """404 Not Found ハンドラ"""
    return jsonify({
        "error": "ページが見つかりません",
        "code": "not_found"
    }), 404

@app.errorhandler(500)
def internal_error(e):
    """500 Internal Server Error ハンドラ"""
    logger.error(f"Internal error: {e}")
    return jsonify({
        "error": "サーバー内部エラーが発生しました",
        "code": "internal_error"
    }), 500

if __name__ == "__main__":
    logger.info(f"Flask app starting on {FLASK_HOST}:{FLASK_PORT}")
    app.run(host=FLASK_HOST, port=FLASK_PORT, debug=FLASK_DEBUG)
