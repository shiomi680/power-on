# GitHub Actions ワークフロー

## 📦 docker-publish.yml

Docker イメージの自動ビルド・テスト・ghcr.io へのアップロード。

### トリガー

- `main` ブランチへの push
- `001-pc-power-control` ブランチへの push
- `v*` タグの push（例: v1.0.0）
- Pull Request to `main`

### ジョブ

1. **build-and-push**
   - Raspberry Pi イメージ + PC イメージをビルド
   - ghcr.io にプッシュ（push イベントのみ）
   - ビルドキャッシュを保存

2. **test**
   - pytest でテスト実行
   - PR でも実行（ghcr.io へはプッシュしない）

### 出力イメージ

```
ghcr.io/your-username/power-on/power-on-rpi:latest
ghcr.io/your-username/power-on/power-on-rpi:main
ghcr.io/your-username/power-on/power-on-rpi:v1.0.0

ghcr.io/your-username/power-on/power-on-pc:latest
ghcr.io/your-username/power-on/power-on-pc:main
ghcr.io/your-username/power-on/power-on-pc:v1.0.0
```

### 詳細

[CI-CD.md](../../docs/CI-CD.md) を参照
