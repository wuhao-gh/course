from datetime import datetime, timedelta
from sqlmodel import SQLModel

import db
from db import engine
from auth import User
from course import Course
from practice import Practice, PracticeAnswer
from homework import Homework, HomeworkAnswer
from progress import Progress
from chat import Message
from sqlmodel import Session

def init_db():
    # 创建数据库表
    SQLModel.metadata.create_all(engine)

    # 使用上下文管理器获取会话
    session = Session(engine)

    # 创建用户
    tea = User(
        name="tea",
        email="teacher@example.com",
        role="teacher",
        status="激活",
        password_hash="$2b$12$.4oOk5iS6h8gFViEW.sHy.toiw240MHGqgXSOvst0aaMYfUjIEhlW",  # password: teacher123
    )
    stu = User(
        name="stu",
        email="student@example.com",
        role="student",
        status="激活",
        password_hash="$2b$12$taQgyQe2VluLbv.5c0ps9ehhV1qo.zK.2ZyZ2hL3VSxDMLCkJ05R6",  # password: student123
    )

    session.add(tea)
    session.add(stu)
    session.commit()

    # 创建课程
    # course1 = Course(
    #     title="Python 基础教程",
    #     description="学习 Python 编程的基础知识",
    #     category="编程语言",
    #     file_path="/courses/python-basics",
    #     creator_id=tea.id
    # )
    # course2 = Course(
    #     title="Web 开发入门",
    #     description="学习使用 FastAPI 开发 Web 应用",
    #     category="Web开发",
    #     file_path="/courses/web-dev",
    #     creator_id=tea.id
    # )
    # session.add(course1)
    # session.add(course2)
    session.commit()

    # 创建练习
    practice1 = Practice(
        title="第一章",
        description="第一章的练习"
    )
    practice2 = Practice(
        title="第二章",
        description="第二章的练习"
    )
    session.add(practice1)
    session.add(practice2)
    session.commit()

    # 创建练习答案
    practice_answer1 = PracticeAnswer(
        practice_id=practice1.id,
        user_id=stu.id,
        file_path="/answers/practice/1/student1.py",
        score=85,
        comment="做得不错，但还需要注意变量命名规范"
    )
    session.add(practice_answer1)
    session.commit()

    # 创建作业
    homework1 = Homework(
        title="第一章",
        description="第一章的作业",
        deadline=datetime.now() + timedelta(days=7)
    )
    homework2 = Homework(
        title="第二章",
        description="第二章的作业",
        deadline=datetime.now() + timedelta(days=14)
    )
    session.add(homework1)
    session.add(homework2)
    session.commit()

    # 创建作业答案
    homework_answer1 = HomeworkAnswer(
        homework_id=homework1.id,
        user_id=stu.id,
        file_path="/answers/homework/1/student1.py",
        score=90,
        comment="项目完成度高，代码结构清晰"
    )
    session.add(homework_answer1)
    session.commit()

    print("数据库初始化完成！")


if __name__ == '__main__':
    db.create_db_and_tables()
    init_db()
