# データモデル: ghcr.io ワンコマンド・デプロイメント

**日付**: 2026-04-29  
**入力**: plan.md Phase 1、research.md の決定事項（シンプル・アプローチ）

## エンティティ・関係図

```
┌─────────────────────────────────────────────────────────────┐
│           DeploymentMethod (デプロイ方法)                    │
├─────────────────────────────────────────────────────────────┤
│ - type: String = "GitClone"                                 │
│ - flow: [git clone → .env設定 → docker compose up]         │
│ - timeEstimate: "5-10 minutes"                              │
└──────────────┬──────────────────────────────────────────────┘
               │ uses
               ▼
┌─────────────────────────────────────────────────────────────┐
│         DockerComposeFile (docker-compose.yml)              │
├─────────────────────────────────────────────────────────────┤
│ - location: String = "repo-root/docker-compose.yml"         │
│ - version: String = "3.8"                                   │
│ - services: [rpi-wol, pc-power]                             │
│ - versionControlled: Boolean = true                         │
│ - inGitRepo: Boolean = true                                 │
│ - references: [ImageSource]                                 │
└──────────────┬──────────────────────────────────────────────┘
               │ contains
               ▼
┌─────────────────────────────────────────────────────────────┐
│        ImageSource (イメージ・ソース)                        │
├─────────────────────────────────────────────────────────────┤
│ - registry: String = "ghcr.io"                              │
│ - owner: String = "shiomi680"                               │
│ - imageName: String = [power-on-rpi | power-on-pc]          │
│ - versionTag: VersionTag                                    │
│ - example: "ghcr.io/shiomi680/power-on-rpi:v1.0.0"          │
└──────────────┬──────────────────────────────────────────────┘
               │ specifies
               ▼
┌─────────────────────────────────────────────────────────────┐
│          VersionTag (バージョン・タグ)                       │
├─────────────────────────────────────────────────────────────┤
│ - tag: String                                               │
│ - type: Enum [semantic (v1.0.0) | latest]                   │
│ - immutable: Boolean                                        │
│                                                             │
│ Examples:                                                   │
│ - v1.0.0 (本番・推奨)                                        │
│ - latest (開発・テスト用のみ)                                │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│        EnvironmentVariable (環境変数)                        │
├─────────────────────────────────────────────────────────────┤
│ - name: String                                              │
│ - defaultValue: String (optional)                           │
│ - required: Boolean                                         │
│ - description: String                                       │
│ - source: String = ".env.example"                           │
│                                                             │
│ Examples:                                                   │
│ - PC_ADDRESS: "192.168.1.100" (required, 環境固有)          │
│ - WOL_TARGET_MAC: "aa:bb:cc:dd:ee:ff" (required, 環境固有)   │
│ - FLASK_PORT: "5000" (default, 通常不変)                     │
│ - LOG_LEVEL: "INFO" (default, 通常不変)                      │
└─────────────────────────────────────────────────────────────┘
```

## エンティティ詳細

### DeploymentMethod

**タイプ**: 値オブジェクト  
**責務**: ユーザーが選択可能なデプロイ方法を定義

```
DeploymentMethod.GitClone:
  - description: "Git リポジトリから full context でデプロイ"
  - targetUser: "Developer、カスタマイズ希望者"
  - steps: ["git clone", "docker compose up"]
  - timeEstimate: "10 minutes"

DeploymentMethod.ReleaseDownload:
  - description: "GitHub Release assets から quick デプロイ"
  - targetUser: "Beginner、最速デプロイ希望者"
  - steps: ["wget docker-compose.yml", "docker compose up"]
  - timeEstimate: "5 minutes"
  - recommended: true
```

### DockerComposeFile

**タイプ**: コンフィグ・エンティティ  
**責務**: Docker Compose 設定の管理

```
root docker-compose.yml:
  - versionControlled: true (git repo)
  - inReleaseAssets: true (GitHub Actions で自動)
  - references: [ImageSource: ghcr.io/shiomi680/power-on-rpi:vX.Y.Z]
  - services: {rpi-wol, pc-power}

rpi-wol/docker-compose.yml:
  - standalone: true
  - references: [ImageSource: ghcr.io/shiomi680/power-on-rpi:vX.Y.Z]

pc-power/docker-compose.yml:
  - standalone: true
  - references: [ImageSource: ghcr.io/shiomi680/power-on-pc:vX.Y.Z]
```

### ImageSource

**タイプ**: 値オブジェクト  
**責務**: Docker イメージ参照（レジストリ + 名前 + タグ）

```
例:
- ghcr.io/shiomi680/power-on-rpi:v1.0.0 (本番・pinned)
- ghcr.io/shiomi680/power-on-rpi:latest (開発・rolling)
- ghcr.io/shiomi680/power-on-pc:v1.0.0 (本番・pinned)

検証ルール:
- registry: ghcr.io（固定）
- owner: shiomi680（固定）
- imageName: power-on-rpi | power-on-pc（required）
- versionTag: 必須（semantic version または latest）
```

### VersionTag

**タイプ**: 値オブジェクト  
**責務**: イメージバージョン指定戦略

```
Type 1: Latest (開発・テスト)
- tag: "latest"
- mutable: true
- use: "Development、テスト環境のみ"
- 警告: "本番では非推奨"

Type 2: Semantic Version (本番・release assets)
- tag: "v1.0.0"（semantic versioning に従う）
- mutable: false
- use: "本番デプロイメント、release assets default"
- 利点: "再現性保証"

Type 3: SHA256 (advanced)
- tag: "sha256:abcd1234..."
- mutable: false
- use: "イミュータブル・イメージID指定（advanced）"
```

### EnvironmentVariable

**タイプ**: 値オブジェクト  
**責務**: .env ファイルで設定される環境変数

```
例:
- PC_ADDRESS (Required)
  - default: "192.168.1.100" (placeholder)
  - description: "PC のネットワーク・アドレス（ユーザーが編集必須）"

- WOL_TARGET_MAC (Required)
  - default: "aa:bb:cc:dd:ee:ff" (placeholder)
  - description: "Wake-On-LAN 対象 MAC アドレス"

- FLASK_PORT (Optional)
  - default: "5000" (固定値)
  - description: "Flask サーバーのポート（通常不変）"

- LOG_LEVEL (Optional)
  - default: "INFO" (固定値)
  - description: "ログ・レベル（通常不変）"
```

## データ・フロー

```
┌──────────────────────────────────────────────────────────┐
│ Developer: code change + docker-compose.yml update       │
└─────────────────┬──────────────────────────────────────┘
                  │ git commit + git push
                  ▼
┌──────────────────────────────────────────────────────────┐
│ GitHub Repository: updated docker-compose.yml            │
│   - image: ghcr.io/shiomi680/power-on-rpi:v1.0.0        │
│   - docker-compose.yml is single source of truth        │
└─────────────────┬──────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│ User: git clone https://github.com/shiomi680/power-on    │
│   └─ Gets full repo with docker-compose.yml             │
└─────────────────┬──────────────────────────────────────┘
                  │
                  ▼
┌──────────────────────────────────────────────────────────┐
│ User: cp .env.example .env                              │
│       (Edit: PC_ADDRESS, WOL_TARGET_MAC)                 │
└─────────────────┬──────────────────────────────────────┘
                  │
                  ▼
         docker compose up -d
```

