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
教师上传练习，查询学生作业完成情况

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

```
├── api                 # 后端服务
│   ├── chat           # 聊天相关接口
│   ├── course         # 课程资料相关接口
│   ├── database       # 数据库配置和模型
│   ├── homework       # 作业相关接口
│   ├── practice       # 练习相关接口
│   ├── stats          # 学习统计相关接口
│   ├── system         # 系统管理相关接口
│   ├── user           # 用户认证相关接口
│   ├── utils          # 工具函数
│   ├── main.py        # FastAPI 应用入口
│   ├── config.py      # 配置文件
│   └── requirements.txt # 后端依赖
├── ui                  # 前端页面
│   ├── public         # 静态资源
│   ├── src            # 源代码
│   │   ├── api       # API 接口封装
│   │   ├── assets    # 资源文件
│   │   ├── components # Vue 组件
│   │   ├── router    # 路由配置
│   │   ├── stores    # Pinia 状态管理
│   │   ├── styles    # 样式文件
│   │   ├── utils     # 工具函数
│   │   ├── views     # 页面组件
│   │   ├── App.vue   # 根组件
│   │   └── main.js   # 入口文件
│   ├── index.html    # HTML 模板
│   ├── package.json  # 前端依赖
│   └── vite.config.js # Vite 配置
├── logs               # 日志目录
├── ops                # 运维相关配置
├── .gitignore        # Git 忽略配置
└── README.md         # 项目说明文档
```

### 运行
1. 准备环境

2. 运行后端服务

3. 运行前端服务

