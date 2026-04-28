FROM python:3.11-slim

ENV PYTHONUNBUFFERED=1 \
    DEBIAN_FRONTEND=noninteractive

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 安装 yt-dlp
RUN curl -L -o /usr/local/bin/yt-dlp https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp && \
    chmod a+rx /usr/local/bin/yt-dlp

WORKDIR /app

# 先复制依赖文件，利用 Docker 缓存
COPY requirements.txt .
RUN pip install --no-cache-dir --timeout 120 -r requirements.txt

# 再复制源码
COPY . .

RUN mkdir -p downloads temp

EXPOSE 8000

# 使用 shell 形式以支持 $PORT 环境变量（Railway 动态分配端口）
CMD uvicorn main:app --host 0.0.0.0 --port ${PORT:-8000} --log-level info
