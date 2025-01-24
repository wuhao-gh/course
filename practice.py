import logging

from fastapi import APIRouter, Depends
from sqlmodel import Session, select, Field, func
from model import BaseEntity
from db import get_session
from auth import get_current_user, User

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

class PracticeStudentView(PracticeBase):
    """练习学生视图"""
    status: str

class PracticeManageView(PracticeBase):
    """练习管理视图"""
    commit_count: int
    total: int


@router.get("", response_model=list[PracticeStudentView])
async def list_practice(session: Session = Depends(get_session), current_user: User = Depends(get_current_user)):
    """获取作业列表"""
    results = session.exec(select(Practice)).all()
    res = []
    for practice in results:
        status = "未提交"
        answer = session.exec(select(PracticeAnswer).where(PracticeAnswer.practice_id == practice.id).where(PracticeAnswer.user_id == current_user.id)).first()
        if answer:
            status = "已提交"
            if answer.score is not None:
                status = "已评分"
        
        practice_view = PracticeStudentView(
            id=practice.id,
            title=practice.title,
            description=practice.description,
            status=status
        )
        res.append(practice_view)
    
    return res

@router.get("/manage/list", response_model=list[PracticeManageView])
async def list_practice_manage(session: Session = Depends(get_session)):
    """获取练习管理列表"""
    results = session.exec(select(Practice)).all()
    res = []
    total_students = session.exec(select(func.count(User.id)).where(User.role == "student")).one()
    for practice in results:
        commit_count = session.exec(select(func.count(func.distinct(PracticeAnswer.user_id))).where(PracticeAnswer.practice_id == practice.id)).one()
        
        practice_view = PracticeManageView(
            id=practice.id,
            title=practice.title,
            description=practice.description,
            commit_count=commit_count,
            total=total_students
        )
        res.append(practice_view)
    return res


@router.get("/{id}")
async def get_practice(id: int, session: Session = Depends(get_session)):
    """获取作业详情"""
    return session.get(Practice, id)


@router.get("/{practice_id}/answer")
async def list_answer(practice_id: int, session: Session = Depends(get_session)):
    """获取练习提交列表"""
    stmt = (
        select(PracticeAnswer, User)
        .join(User, PracticeAnswer.user_id == User.id)
        .where(PracticeAnswer.practice_id == practice_id)
    )
    results = session.exec(stmt).all()
    return [
        {
            "id": answer.id,
            "practice_id": answer.practice_id,
            "file_path": answer.file_path,
            "score": answer.score,
            "comment": answer.comment,
            "created_at": answer.created_at,
            "user": {
                "id": user.id,
                "name": user.name
            }
        }
        for answer, user in results
    ]


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
