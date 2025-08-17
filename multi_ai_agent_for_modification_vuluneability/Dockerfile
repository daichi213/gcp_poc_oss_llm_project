# ベースイメージ
FROM python:3.11-slim

# 作業ディレクトリの設定
WORKDIR /app

# 必要なライブラリをインストール
COPY app/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# エージェントのソースコードをコピー
COPY app/ .

# コンテナ実行時のデフォルトコマンド
ENTRYPOINT ["python", "main.py"]
