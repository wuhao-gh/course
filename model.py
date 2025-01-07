from datetime import datetime
from typing import Union

from sqlmodel import Field, SQLModel


class BaseEntity(SQLModel):
    id: Union[int, None] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=datetime.now)
    updated_at: datetime = Field(default_factory=datetime.now)



