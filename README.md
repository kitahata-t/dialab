# DiaLab

研究室向けに GPT ベースの対話システムを提供する Streamlit アプリです。独自のユーザー管理（パスワード認証）とユーザー単位でのチャットログ保存に対応しています。

## 構成概要

- フロントエンド: Streamlit (`streamlit_app.py`)
- バックエンド: SQLite によるユーザー・チャットログ管理 (`app/database.py`)
- 認証: パスワードハッシュ化による独自ログイン (`app/auth.py`)
- モデル: OpenAI Chat Completions API（デフォルト `gpt-4o-mini`）

## セットアップ

1. 依存関係のインストール
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   pip install -r requirements.txt
   ```
2. 環境変数ファイルの準備
   ```bash
   cp .env.example .env
   ```
   `.env` に `OPENAI_API_KEY` などを設定します。
3. 初期ユーザーの作成
   ```bash
   python scripts/create_user.py --username myuser
   ```

ローカル実行:

```bash
streamlit run streamlit_app.py
```

`http://localhost:8501` にアクセスしてログインしてください。

## Docker での運用

### ビルドと起動

```bash
docker compose build
docker compose up -d
```

- `.env` の値がコンテナ内に反映されます。
- `data/` ディレクトリはコンテナと共有され、SQLite の DB ファイルが保存されます。
- 利用ポートは `8501`（必要に応じて `docker-compose.yml` を編集してください）。
- 初回ユーザー作成がまだの場合は次を実行してください:
  ```bash
  docker compose run --rm dialab python scripts/create_user.py --username myuser
  ```

### 停止

```bash
docker compose down
```

## ディレクトリ

- `app/` Streamlit アプリ本体とユーティリティ
- `scripts/` 運用用スクリプト（ユーザー作成など）
- `data/` SQLite データファイル（初回起動時に作成）

## その他

- 使用モデルを切り替える場合は環境変数 `OPENAI_MODEL` を設定してください。
- 追加の監査や可視化が必要な場合は `chat_logs` テーブルを参照してください。
