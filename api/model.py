from datetime import datetime

from sqlmodel import SQLModel, Field


class BaseEntity(SQLModel):
    id: int | None = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)


class CourseProgress(BaseEntity, table=True):
    """课程进度"""
    course_id: int = Field(foreign_key="course.id")
    user_id: int = Field(foreign_key="user.id")
    progress: float = Field(default=0)  # 播放进度（百分比）
    current_time: float = Field(default=0)  # 当前播放时间（秒）
    duration: float = Field(default=0)  # 视频总时长（秒）
    is_completed: bool = Field(default=False)  # 是否完成观看
