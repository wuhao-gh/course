from sqlmodel import Session, SQLModel, create_engine
import os

# 获取数据库路径
current_dir = os.path.dirname(os.path.abspath(__file__))
db_path = os.path.join(current_dir, "course.db")
DATABASE_URL = f"sqlite:///{db_path}"

# 创建数据库引擎
engine = create_engine(DATABASE_URL, echo=True)

def create_db_and_tables():
    """创建数据库表"""
    SQLModel.metadata.create_all(engine)

def get_session():
    """获取数据库会话"""
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception as e:
            session.rollback()
            raise e

