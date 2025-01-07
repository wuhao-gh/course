import os
import time
import uuid
from typing import List
from fastapi import APIRouter, Depends, UploadFile, File, Form, HTTPException
from sqlmodel import Session, select

from db import get_session
from model import BaseEntity
from admin import User

router = APIRouter(prefix="/api/course", tags=["课程接口"])


def generate_unique_filename(original_filename: str) -> str:
    """生成唯一的文件名"""
    # 分离文件名和扩展名
    name, ext = os.path.splitext(original_filename)
    # 生成时间戳和随机字符串
    timestamp = time.strftime("%Y%m%d_%H%M%S")
    random_str = str(uuid.uuid4())[:8]
    # 组合新文件名：原文件名_时间戳_随机字符串.扩展名
    return f"{name}_{timestamp}_{random_str}{ext}"


def is_valid_file(filename: str) -> bool:
    """检查文件是否为有效的视频或PDF文件"""
    # 获取文件扩展名（转小写）
    ext = filename.lower().split('.')[-1]
    # 支持的视频格式
    video_extensions = {'mp4', 'webm', 'ogg', 'mov', 'avi', 'wmv', 'flv', 'm4v', 'mkv'}
    # 支持的文档格式
    document_extensions = {'pdf'}
    
    return ext in video_extensions or ext in document_extensions


@router.get("/categories", response_model=List[str])
async def get_categories(session: Session = Depends(get_session)):
    """获取所有课程分类"""
    # 从数据库中查询所有不同的分类
    result = session.exec(select(Course.category).distinct()).all()
    return sorted(result) if result else []


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
    # 检查文件大小（100MB 限制）
    file_size = 0
    chunk_size = 1024 * 1024  # 1MB chunks
    while chunk := await file.read(chunk_size):
        file_size += len(chunk)
        if file_size > 100 * 1024 * 1024:  # 100MB
            raise HTTPException(status_code=400, detail="文件大小不能超过 100MB")
    
    # 重置文件指针
    await file.seek(0)
    
    # 验证文件类型
    if not is_valid_file(file.filename):
        raise HTTPException(status_code=400, detail="只支持视频文件或 PDF 文件")
    
    # 确保目录存在
    dir = "ops/upload/"
    os.makedirs(dir, exist_ok=True)
    
    # 生成唯一文件名
    unique_filename = generate_unique_filename(file.filename)
    file_path = os.path.join(dir, unique_filename)
    
    # 保存文件
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # 创建课程记录
    entity = Course(title=title, description=description, category=category, 
                   file_path=unique_filename, creator_id=1)
    session.add(entity)
    session.commit()
    return entity


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
