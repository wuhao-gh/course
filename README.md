## course

### 需求描述

#### 用户与角色权限

学生角色包含的权限：

- 课程资料（仅查看）
- 练习
- 作业
- 学习统计（仅查看自己数据）
- 问答

教师角色包含的权限
- 课程资料（可上传）
- 练习管理
- 作业管理
- 学习统计（可查看所有学生的数据）
- 问答
- 系统管理

使用用户名密码登陆系统

所有页面均需要登录才能查看

#### 课程资料

教师：通过上传视频、PDF 创建课程资料

学生：观看视频、PDF

记录学生观看进度，用于统计分析

#### 练习管理
教师上传练习、查询学生作业完成情况

#### 练习

展示教师上传的练习，学生上传答案

#### 作业管理

教师上传作业，给学生上传的答案打分及点评

#### 作业
学生查看作业并上传答案

#### 学习统计
教师查看所有学生的学习统计数据

学生查看自己的学习统计数据

#### 问答
师生互动交流

#### 系统管理
教师管理系统中的用户


### 技术选型

#### 前端
[Vue3](https://cn.vuejs.org/)

[Element Plus](https://element-plus.org/zh-CN/)

#### 后端
使用 [uv](https://github.com/astral-sh/uv) 管理 Python 版本和包

[FastAPI](https://fastapi.tiangolo.com/zh/)

ORM：[SQLModel](https://sqlmodel.cn/)

### 目录结构
```text
course/
├── README.md                 # 项目说明文档
├── pyproject.toml           # Python 项目配置文件
├── uv.lock                  # uv 依赖锁定文件
├── .python-version          # Python 版本配置
├── main.py                  # FastAPI 应用入口
├── model.py                 # 数据模型定义
├── db.py                    # 数据库配置
├── auth.py                  # 认证相关
├── course.py                # 课程相关接口
├── homework.py              # 作业相关接口
├── practice.py              # 练习相关接口
├── progress.py              # 学习进度相关接口
├── chat.py                  # 问答功能接口
├── stat.py                  # 统计相关接口
├── admin.py                 # 系统管理接口
├── logger.py                # 日志配置
├── init_db.py              # 数据库初始化脚本
│
└── ui/                      # 前端代码
    ├── index.html          # 入口 HTML
    ├── package.json        # 前端依赖配置
    ├── vite.config.js      # Vite 配置
    ├── uno.config.ts       # UnoCSS 配置
    ├── src/
    │   ├── main.js         # 应用入口
    │   ├── App.vue         # 根组件
    │   ├── router/         # 路由配置
    │   ├── stores/         # Pinia 状态管理
    │   ├── api/            # API 接口封装
    │   ├── components/     # 公共组件
    │   ├── utils/          # 工具函数
    │   ├── views/          # 页面组件
    │   └── assets/         # 静态资源
    └── public/             # 公共静态资源
```
### 本地运行
1. 准备环境
- 安装 uv
- uv sync
- 安装 node.js
- 安装 pnpm

2. 运行后端服务
```bash
python main.py
```

3. 运行前端服务
```bash
cd ui
pnpm install
pnpm run dev
```

### docker 运行
```bash
docker build -t course-app . && docker run -p 8000:8000 course-app
```