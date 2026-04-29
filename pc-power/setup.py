from setuptools import setup, find_packages

setup(
    name="power-on-pc",
    version="0.1.0",
    description="PC 電源管理サービス - Flask API + シャットダウンコマンド",
    author="genki",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "Flask==2.3.3",
        "requests==2.31.0",
    ],
    extras_require={
        "dev": [
            "pytest==7.4.0",
            "pytest-cov==4.1.0",
        ]
    },
    entry_points={
        "console_scripts": [
            "power-on-pc=cli:main",
        ],
    },
)
