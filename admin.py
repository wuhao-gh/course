import logging

import bcrypt
from fastapi import APIRouter, Depends
from sqlmodel import select

from auth import User, UserCreate
from db import get_session

router = APIRouter(prefix="/api/admin", tags=["管理"])
logger = logging.getLogger(__name__)


def hash_password(password: str) -> str:
    """对密码进行哈希处理"""
    salt = bcrypt.gensalt()
    return bcrypt.hashpw(password.encode(), salt).decode()


def verify_password(password: str, hashed: str) -> bool:
    """验证密码"""
    return bcrypt.checkpw(password.encode(), hashed.encode())


@router.post("")
async def create_user(user_create: UserCreate, session=Depends(get_session)):
    """创建用户"""
    user = User(**user_create.model_dump())
    user.password_hash = hash_password(user_create.password)
    session.add(user)


@router.get("")
async def list_user(session=Depends(get_session)):
    """获取用户列表"""
    return session.exec(select(User)).all()


@router.get("/{id}")
async def get_user(id: int, session=Depends(get_session)):
    """获取用户详情"""
    return session.get(User, id)


