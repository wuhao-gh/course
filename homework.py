import logging
from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select, Field, and_
from sqlalchemy import func

from model import BaseEntity
from auth import UserView, User, get_current_user
from db import get_session
from pydantic import BaseModel

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
    """作业管理视图"""
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


class HomeworkStudentView(HomeworkBase):
    """作业学生视图"""
    status: str
    answer: HomeworkAnswerView | None = None


class HomeworkAnswerScore(BaseModel):
    """作业评分"""
    score: int = Field(ge=0, le=100)
    comment: str | None = None


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


# 学生视角查看作业列表
@router.get("/student", response_model=list[HomeworkStudentView])
async def list_student_homework(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """获取作业列表"""
    # 使用 left outer join 查询作业和当前用户的答案
    query = (
        select(Homework, HomeworkAnswer)
        .outerjoin(HomeworkAnswer, and_(
            HomeworkAnswer.homework_id == Homework.id,
            HomeworkAnswer.user_id == current_user.id
        ))
        .order_by(Homework.id)
    )
    results = session.exec(query).all()
    
    # 转换查询结果为 HomeworkStudentView 格式
    res = []
    for homework, answer in results:
        status = "pending"
        answer_view = None
        if answer:
            status = "submitted"
            if answer.score is not None:
                status = "graded"
                
            answer_view = HomeworkAnswerView(
                id=answer.id,
                homework_id=answer.homework_id,
                user_id=answer.user_id,
                file_path=answer.file_path,
                score=answer.score,
                comment=answer.comment
            )
        
        homework_view = HomeworkStudentView(
            id=homework.id,
            title=homework.title,
            description=homework.description,
            deadline=homework.deadline,
            status=status,
            answer=answer_view
        )
        res.append(homework_view)
    
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


@router.put("/answer/{answer_id}/score")
async def score_homework_answer(
    answer_id: int,
    score: HomeworkAnswerScore,
    session: Session = Depends(get_session),
    current_user: User = Depends(get_current_user)
):
    """评分作业"""
    # 检查当前用户是否为教师
    if current_user.role != "teacher":
        raise HTTPException(status_code=403, detail="只有教师可以评分")

    # 查找作业答案
    answer = session.get(HomeworkAnswer, answer_id)
    if not answer:
        raise HTTPException(status_code=404, detail="作业答案不存在")

    # 更新分数和评语
    answer.score = score.score
    answer.comment = score.comment
    session.add(answer)
    session.commit()

    return {"message": "评分成功"}
