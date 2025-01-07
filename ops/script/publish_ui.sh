#!/bin/bash

# 从环境变量获取配置
REMOTE_USER="${DEPLOY_USER:?'请设置 DEPLOY_USER 环境变量'}"
REMOTE_HOST="${DEPLOY_HOST:?'请设置 DEPLOY_HOST 环境变量'}"
REMOTE_PATH="/opt/deploy/static/"
UI_DIR="ui"

# 确保在项目根目录执行
if [ ! -d "$UI_DIR" ]; then
  echo "错误: 请在项目根目录执行此脚本"
  exit 1
fi

# 进入 UI 目录
cd $UI_DIR

# 安装依赖并构建
# echo "📦 安装依赖..."
# pnpm install

echo "🔨 构建项目..."
pnpm run build

# 检查构建是否成功
if [ ! -d "dist" ]; then
  echo "❌ 构建失败: dist 目录不存在"
  exit 1
fi

# 压缩 dist 目录
echo "🗜️ 压缩 dist 目录..."
tar -czf dist.tar.gz dist/

# 传输文件
echo "📤 上传到服务器..."
scp dist.tar.gz $REMOTE_USER@$REMOTE_HOST:$REMOTE_PATH/

# 执行远程命令
echo "📂 在服务器解压文件..."
ssh $REMOTE_USER@$REMOTE_HOST "cd $REMOTE_PATH && \
  rm -rf course/ && \
  tar -xzf dist.tar.gz && \
  mv dist course && \
  rm dist.tar.gz"

# 清理本地文件
echo "🧹 清理本地文件..."
rm dist.tar.gz
rm -rf dist

echo "✅ 部署完成！"
