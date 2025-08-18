# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# 非rootユーザーの作成
RUN groupadd -r appuser && useradd -r -g appuser -d /app -s /sbin/nologin -c "Docker image user" appuser

# 必要なライブラリをインストール
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# エージェントのソースコードをコピー
COPY app/ .

# ディレクトリの所有権を変更
RUN chown -R appuser:appuser /app

# ユーザーの切り替え
USER appuser

# コンテナ実行時のデフォルトコマンド
ENTRYPOINT ["python", "main.py"]