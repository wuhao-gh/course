import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, Field

from model import BaseEntity
from db import get_session

router = APIRouter(prefix="/api/practice", tags=["练习管理"])
logger = logging.getLogger(__name__)

class PracticeBase(BaseEntity):
    """练习模型"""
    title: str
    description: str

class Practice(PracticeBase, table=True):
    """练习模型"""


class PracticeAnswerBase(BaseEntity):
    """练习答案"""
    practice_id: int = Field(foreign_key="practice.id")
    user_id: int = Field(foreign_key="user.id")
    file_path: str
    score: float | None = None
    comment: str | None = None

class PracticeAnswer(PracticeAnswerBase, table=True):
    """练习答案"""
    practice_id: int = Field(foreign_key="practice.id")
    user_id: int = Field(foreign_key="user.id")
    file_path: str
    score: float | None = None
    comment: str | None = None


@router.get("")
async def list_practice(session: Session = Depends(get_session)):
    """获取作业列表"""
    return session.exec(select(Practice)).all()


@router.get("/{id}")
async def get_practice(id: int, session: Session = Depends(get_session)):
    """获取作业详情"""
    return session.get(Practice, id)


@router.get("/answer/{practice_id}")
async def list_answer(practice_id: int, session: Session = Depends(get_session)):
    """获取练习提交列表"""
    return session.exec(select(PracticeAnswer).where(PracticeAnswer.practice_id == practice_id)).all()


@router.post("")
async def create_practice(practice: PracticeAnswer, session: Session = Depends(get_session)):
    """创建练习"""
    session.add(practice)


@router.post("/answer")
async def submit_practice(practice_answer: PracticeAnswer, session: Session = Depends(get_session)):
    """提交练习答案"""
    session.add(practice_answer)


@router.put("/{practice_id}/score/{answer_id}")
async def score_practice_answer(session: Session = Depends(get_session)):
    """评分练习答案"""
