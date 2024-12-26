from fastapi import APIRouter, Depends
from sqlmodel import Session, select, func
from datetime import datetime, timedelta

from db import get_session
from model import CourseProgress
from course import Course
from admin import User

router = APIRouter(prefix="/progress", tags=["progress"])


@router.get("/{course_id}")
async def get_progress(course_id: int, user_id: int, session: Session = Depends(get_session)):
    """获取课程进度"""
    progress = session.exec(
        select(CourseProgress)
        .where(CourseProgress.course_id == course_id)
        .where(CourseProgress.user_id == user_id)
    ).first()
    return progress


@router.post("")
async def save_progress(progress: CourseProgress, session: Session = Depends(get_session)):
    """保存课程进度"""
    existing = session.exec(
        select(CourseProgress)
        .where(CourseProgress.course_id == progress.course_id)
        .where(CourseProgress.user_id == progress.user_id)
    ).first()

    if existing:
        existing.progress = progress.progress
        existing.current_time = progress.current_time
        existing.duration = progress.duration
        existing.is_completed = progress.is_completed
        session.add(existing)
    else:
        session.add(progress)

    session.commit()
    session.refresh(progress if not existing else existing)
    return progress if not existing else existing


@router.get("/stats/overview")
async def get_progress_overview(session: Session = Depends(get_session)):
    """获取总体学习概览"""
    # 总课程数
    total_courses = session.exec(select(func.count()).select_from(Course)).one()
    # 总学习人数
    total_learners = session.exec(select(func.count(func.distinct(CourseProgress.user_id))).select_from(CourseProgress)).one()
    # 总学习时长（小时）
    total_hours = session.exec(
        select(func.sum(CourseProgress.current_time) / 3600).select_from(CourseProgress)
    ).one() or 0
    # 完成课程数
    completed_courses = session.exec(
        select(func.count()).select_from(CourseProgress).where(CourseProgress.is_completed == True)
    ).one()

    return {
        "total_courses": total_courses,
        "total_learners": total_learners,
        "total_hours": round(total_hours, 1),
        "completed_courses": completed_courses
    }


@router.get("/stats/course/{course_id}")
async def get_course_stats(course_id: int, session: Session = Depends(get_session)):
    """获取单个课程的学习统计"""
    # 学习人数
    learner_count = session.exec(
        select(func.count(func.distinct(CourseProgress.user_id)))
        .where(CourseProgress.course_id == course_id)
    ).one()

    # 完成人数
    completed_count = session.exec(
        select(func.count(func.distinct(CourseProgress.user_id)))
        .where(CourseProgress.course_id == course_id)
        .where(CourseProgress.is_completed == True)
    ).one()

    # 平均观看进度
    avg_progress = session.exec(
        select(func.avg(CourseProgress.progress))
        .where(CourseProgress.course_id == course_id)
    ).one() or 0

    # 平均观看时长
    avg_watch_time = session.exec(
        select(func.avg(CourseProgress.current_time))
        .where(CourseProgress.course_id == course_id)
    ).one() or 0

    return {
        "learner_count": learner_count,
        "completed_count": completed_count,
        "completion_rate": round(completed_count / learner_count * 100 if learner_count > 0 else 0, 1),
        "avg_progress": round(avg_progress, 1),
        "avg_watch_time": round(avg_watch_time / 60, 1)  # 转换为分钟
    }


@router.get("/stats/trend")
async def get_learning_trend(days: int = 7, session: Session = Depends(get_session)):
    """获取学习趋势"""
    start_date = datetime.now() - timedelta(days=days)

    # 每日学习人数
    daily_learners = session.exec(
        select(
            func.date(CourseProgress.created_at).label("date"),
            func.count(func.distinct(CourseProgress.user_id)).label("count")
        )
        .where(CourseProgress.created_at >= start_date)
        .group_by(func.date(CourseProgress.created_at))
        .order_by("date")
    ).all()

    # 每日完成课程数
    daily_completions = session.exec(
        select(
            func.date(CourseProgress.updated_at).label("date"),
            func.count().label("count")
        )
        .where(CourseProgress.updated_at >= start_date)
        .where(CourseProgress.is_completed == True)
        .group_by(func.date(CourseProgress.updated_at))
        .order_by("date")
    ).all()

    return {
        "daily_learners": [{"date": str(d[0]), "count": d[1]} for d in daily_learners],
        "daily_completions": [{"date": str(d[0]), "count": d[1]} for d in daily_completions]
    }


@router.get("/stats/user/{user_id}")
async def get_user_learning_stats(user_id: int, session: Session = Depends(get_session)):
    """获取用户学习统计"""
    # 学习课程数
    course_count = session.exec(
        select(func.count(func.distinct(CourseProgress.course_id)))
        .where(CourseProgress.user_id == user_id)
    ).one()

    # 完成课程数
    completed_count = session.exec(
        select(func.count(func.distinct(CourseProgress.course_id)))
        .where(CourseProgress.user_id == user_id)
        .where(CourseProgress.is_completed == True)
    ).one()

    # 总学习时长
    total_time = session.exec(
        select(func.sum(CourseProgress.current_time))
        .where(CourseProgress.user_id == user_id)
    ).one() or 0

    # 最近学习的课程
    recent_courses = session.exec(
        select(Course)
        .join(CourseProgress, CourseProgress.course_id == Course.id)
        .where(CourseProgress.user_id == user_id)
        .order_by(CourseProgress.updated_at.desc())
        .limit(5)
    ).all()

    return {
        "course_count": course_count,
        "completed_count": completed_count,
        "completion_rate": round(completed_count / course_count * 100 if course_count > 0 else 0, 1),
        "total_time": round(total_time / 3600, 1),  # 转换为小时
        "recent_courses": [
            {
                "id": course.id,
                "title": course.title,
                "last_progress": session.exec(
                    select(CourseProgress.progress)
                    .where(CourseProgress.course_id == course.id)
                    .where(CourseProgress.user_id == user_id)
                ).one()
            }
            for course in recent_courses
        ]
    }
