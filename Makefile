.PHONY: help install install-dev test lint clean run-rpi run-pc setup

help:
	@echo "power-on プロジェクト Makefile"
	@echo ""
	@echo "利用可能なコマンド:"
	@echo "  make install      - 依存パッケージをインストール"
	@echo "  make install-dev  - 開発用依存パッケージをインストール"
	@echo "  make test         - テストを実行"
	@echo "  make lint         - コードスタイルをチェック"
	@echo "  make clean        - ビルドアーティファクトを削除"
	@echo "  make run-rpi      - Raspberry Pi サーバーを起動"
	@echo "  make run-pc       - PC サーバーを起動"

# インストール
install:
	cd rpi-wol && pip install -q -r requirements.txt
	cd pc-power && pip install -q -r requirements.txt

install-dev:
	cd rpi-wol && pip install -q -r requirements.txt -e ".[dev]"
	cd pc-power && pip install -q -r requirements.txt -e ".[dev]"

# テスト
test:
	@echo "=== Raspberry Pi WOL テスト ==="
	cd rpi-wol && pytest tests/ -v
	@echo ""
	@echo "=== PC 電源管理テスト ==="
	cd pc-power && pytest tests/ -v

test-cov:
	@echo "=== テストカバレッジレポート ==="
	cd rpi-wol && pytest tests/ --cov=src --cov-report=html
	cd pc-power && pytest tests/ --cov=src --cov-report=html
	@echo "Coverage reports generated in rpi-wol/htmlcov and pc-power/htmlcov"

# Lint（コードスタイルチェック）
lint:
	@echo "=== Raspberry Pi WOL lint ==="
	cd rpi-wol && python -m py_compile src/**/*.py || true
	@echo ""
	@echo "=== PC 電源管理 lint ==="
	cd pc-power && python -m py_compile src/**/*.py || true

# クリーンアップ
clean:
	find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	find . -type f -name "*.pyc" -delete
	find . -type d -name "*.egg-info" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".pytest_cache" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name ".coverage" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "htmlcov" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "build" -exec rm -rf {} + 2>/dev/null || true
	find . -type d -name "dist" -exec rm -rf {} + 2>/dev/null || true
	@echo "Clean complete"

# サーバー起動
run-rpi:
	cd rpi-wol && python src/flask_app.py

run-pc:
	cd pc-power && python src/flask_app.py

# セットアップ
setup: install-dev
	@echo "Setup complete. Run 'make test' to verify installation."
