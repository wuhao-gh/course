# 第一阶段：构建前端
FROM node:20-slim AS frontend-builder

# 安装 pnpm
RUN npm install -g pnpm

# 设置工作目录
WORKDIR /app

# 复制前端项目文件
COPY ui/package.json ui/pnpm-lock.yaml ./

# 安装依赖
RUN pnpm install

# 复制源代码
COPY ui/ ./

# 构建前端
RUN pnpm run build

# 第二阶段：Python 后端
FROM python:3.12-slim

# 设置工作目录
WORKDIR /app

# 安装系统依赖
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# 安装 Python 依赖
RUN pip install "bcrypt>=4.2.1" \
    "fastapi>=0.115.6" \
    "passlib[bcrypt]>=1.7.4" \
    "pyjwt>=2.10.1" \
    "python-multipart>=0.0.19" \
    "sqlmodel>=0.0.22" \
    "uvicorn[standard]>=0.32.1" \
    "websockets>=14.1"

# 复制后端源码
COPY *.py ./

# 创建必要的目录
RUN mkdir -p ops/upload ops/db && \
    touch ops/db/course.db && \
    chmod 777 ops/db/course.db

# 复制前端构建产物
COPY --from=frontend-builder /app/dist /app/ui/dist

# 设置环境变量
ENV PYTHONPATH=/app
ENV PORT=8000

# 暴露端口
EXPOSE 8000

# 初始化数据库并启动应用
COPY docker-entrypoint.sh /
RUN chmod +x /docker-entrypoint.sh
ENTRYPOINT ["/docker-entrypoint.sh"]
