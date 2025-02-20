from sqlmodel import SQLModel, Field
from typing import List, ClassVar
from .base import SequenceItemBase
from .user import UserRole
from sqlalchemy import Column, String
from sqlalchemy.dialects.postgresql import ARRAY

class HomeworkTask(SequenceItemBase, table=True):
    id_prefix: ClassVar[str] = "hw"

    teacher_id: str = Field(foreign_key="user.id")
    student_ids: List[str] = Field(
        default_factory=list,
        sa_column=Column(ARRAY(String))
    )

    class Config:
        from_attributes = True
