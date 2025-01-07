from datetime import datetime, timedelta
from sqlmodel import SQLModel

import db
import model
from db import engine, get_session
from model import Role, User, Course, Practice, PracticeAnswer, Homework, HomeworkAnswer
from sqlmodel import Session

def init_db():
    # 创建数据库表
    SQLModel.metadata.create_all(engine)

    # 使用上下文管理器获取会话
    session = Session(engine)
    # 创建角色
    admin_role = Role(name="管理员")
    teacher_role = Role(name="教师")
    student_role = Role(name="学生")
    session.add(admin_role)
    session.add(teacher_role)
    session.add(student_role)
    session.commit()

    # 创建用户
    admin = User(
        name="Admin User",
        email="admin@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.5IMwxfKCCrFi",  # password: admin123
        role_id=admin_role.id
    )
    teacher = User(
        name="Teacher User",
        email="teacher@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.5IMwxfKCCrFi",  # password: teacher123
        role_id=teacher_role.id
    )
    student = User(
        name="Student User",
        email="student@example.com",
        password_hash="$2b$12$LQv3c1yqBWVHxkd0LHAkCOYz6TtxMQJqhN8/LewY.5IMwxfKCCrFi",  # password: student123
        role_id=student_role.id
    )
    session.add(admin)
    session.add(teacher)
    session.add(student)
    session.commit()

    # 创建课程
    course1 = Course(
        title="Python 基础教程",
        description="学习 Python 编程的基础知识",
        category="编程语言",
        file_path="/courses/python-basics",
        creator_id=teacher.id
    )
    course2 = Course(
        title="Web 开发入门",
        description="学习使用 FastAPI 开发 Web 应用",
        category="Web开发",
        file_path="/courses/web-dev",
        creator_id=teacher.id
    )
    session.add(course1)
    session.add(course2)
    session.commit()

    # 创建练习
    practice1 = Practice(
        title="Python 变量练习",
        description="完成关于 Python 变量的练习题"
    )
    practice2 = Practice(
        title="函数编写练习",
        description="编写几个简单的 Python 函数"
    )
    session.add(practice1)
    session.add(practice2)
    session.commit()

    # 创建练习答案
    practice_answer1 = PracticeAnswer(
        practice_id=practice1.id,
        user_id=student.id,
        file_path="/answers/practice/1/student1.py",
        score=85,
        comment="做得不错，但还需要注意变量命名规范"
    )
    session.add(practice_answer1)
    session.commit()

    # 创建作业
    homework1 = Homework(
        title="Python 项目实战",
        description="开发一个简单的命令行工具",
        deadline=datetime.now() + timedelta(days=7)
    )
    homework2 = Homework(
        title="Web API 开发",
        description="使用 FastAPI 开发一个 REST API",
        deadline=datetime.now() + timedelta(days=14)
    )
    session.add(homework1)
    session.add(homework2)
    session.commit()

    # 创建作业答案
    homework_answer1 = HomeworkAnswer(
        homework_id=homework1.id,
        user_id=student.id,
        file_path="/answers/homework/1/student1.py",
        score=90,
        comment="项目完成度高，代码结构清晰"
    )
    session.add(homework_answer1)
    session.commit()

    print("数据库初始化完成！")


# if __name__ == '__main__':
    # db.create_db_and_tables()
    # init_db()
