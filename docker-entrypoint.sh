#!/bin/sh
set -e

# 初始化数据库
python init_db.py

# 启动应用
exec python main.py
