import logging
from datetime import datetime

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, Field
from sqlalchemy import func

from model import BaseEntity
from auth import UserView, User
from db import get_session

router = APIRouter(prefix="/api/homework", tags=["作业管理"])
logger = logging.getLogger(__name__)


class HomeworkBase(BaseEntity):
    """作业"""
    title: str
    description: str
    deadline: datetime

class HomeworkCreate(HomeworkBase):
    """创建作业"""


class Homework(HomeworkBase, table=True):
    """作业"""
    title: str
    description: str
    deadline: datetime


class HomeworkView(HomeworkBase):
    """作业答案视图"""
    answer_count: int | None = None
    score_count: int | None = None
    user_count: int | None = None


class HomeworkAnswerBase(BaseEntity):
    """作业答案"""
    homework_id: int = Field(foreign_key="homework.id")
    user_id: int = Field(foreign_key="user.id")
    file_path: str | None = None
    score: int | None = None
    comment: str | None = None

class HomeworkAnswer(HomeworkAnswerBase, table=True):
    """作业答案"""

class HomeworkAnswerView(HomeworkAnswerBase):
    """作业答案"""
    user: UserView | None = None


@router.get("", response_model=list[HomeworkView])
async def list_homework(session: Session = Depends(get_session)):
    """获取作业列表"""
    all_homework = session.exec(select(Homework).order_by(Homework.id)).all()
    user_count = session.exec(select(func.count()).select_from(User).where(User.role == "student")).one()
    res = []
    for homework in all_homework:
        view = HomeworkView.model_validate(homework)
        view.answer_count = session.exec(select(func.count()).select_from(HomeworkAnswer).where(HomeworkAnswer.homework_id == homework.id)).one()
        view.score_count = session.exec(select(func.count()).select_from(HomeworkAnswer).where(HomeworkAnswer.homework_id == homework.id).where(HomeworkAnswer.score != None)).one()
        view.user_count = user_count
        res.append(view)
    return res


@router.get("/{id}")
async def get_homework(id: int, session: Session = Depends(get_session)):
    """获取作业详情"""
    return session.get(Homework, id)


@router.get("/{homework_id}/answer", response_model=list[HomeworkAnswerView])
async def list_answer(homework_id: int, session: Session = Depends(get_session)):
    """获取答案列表"""
    all_answer: list[HomeworkAnswer] = session.exec(select(HomeworkAnswer).where(HomeworkAnswer.homework_id == homework_id)).all()
    res = []
    for answer in all_answer:
        answer_view = HomeworkAnswerView.model_validate(answer)
        user = session.get(User, answer.user_id)
        answer_view.user = UserView.model_validate(user)
        res.append(answer_view)
    return res


@router.post("")
async def create_homework(homework_create: HomeworkCreate, session: Session = Depends(get_session)):
    """创建作业"""
    homework = Homework.model_validate(homework_create)
    session.add(homework)


@router.post("/answer")
async def submit_homework(homeworkAnswer: HomeworkAnswer, session: Session = Depends(get_session)):
    """提交作业"""
    session.add(homeworkAnswer)


@router.put("/{homework_id}/score/{answer_id}")
async def score_homework_answer(session: Session = Depends(get_session)):
    """评分作业"""
