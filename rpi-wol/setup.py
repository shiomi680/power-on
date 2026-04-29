from setuptools import setup, find_packages

setup(
    name="power-on-rpi",
    version="0.1.0",
    description="Raspberry Pi WOL サービス - Web UI ホスティング + WOL パケット送信",
    author="genki",
    packages=find_packages(where="src"),
    package_dir={"": "src"},
    python_requires=">=3.10",
    install_requires=[
        "Flask==2.3.3",
        "scapy==2.4.5",
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
            "power-on-rpi=cli:main",
        ],
    },
)
