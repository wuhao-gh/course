import os

from fastapi import APIRouter, Depends, UploadFile, File, Form
from sqlmodel import Session, select

from db import get_session
from model import BaseEntity
from admin import User

router = APIRouter(prefix="/api/course", tags=["课程接口"])


class CourseBase(BaseEntity):
    """课程模型"""
    title: str
    description: str
    category: str
    file_path: str
    creator_id: int


class Course(CourseBase, table=True):
    """课程数据库映射"""


class CourseView(CourseBase):
    """课程视图"""
    creator: User


class CourseCreate(CourseBase):
    """创建课程"""
    file: UploadFile


@router.post("")
async def create_course(file: UploadFile = File(), title: str = Form(), description: str = Form(),
                        category: str = Form(),
                        session: Session = Depends(get_session)):
    """创建课程"""
    dir = "./upload/"
    os.makedirs(dir, exist_ok=True)
    file_path = dir + file.filename
    with open(file_path, "wb") as f:
        f.write(file.file.read())

    entity = Course(title=title, description=description, category=category, file_path=file.filename, creator_id=1)
    session.add(entity)


@router.get("")
async def list_course(category: str | None = None, session: Session = Depends(get_session)):
    """获取课程列表"""
    s = select(Course)
    if category:
        s = s.where(Course.category == category)
    return session.exec(s).all()


@router.get("/{id}", response_model=CourseView)
async def get_course(id: int, session: Session = Depends(get_session)):
    """获取课程详情"""
    return session.get(Course, id)


@router.delete("/{id}")
async def delete_course(id: int, session: Session = Depends(get_session)):
    """删除课程"""
    course = session.get(Course, id)
    session.delete(course)
