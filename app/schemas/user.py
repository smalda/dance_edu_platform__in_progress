from enum import Enum
from sqlmodel import SQLModel, Field
from .base import TimeStampedModel
from typing import Optional, Dict, ClassVar
from sqlalchemy import JSON

class UserRole(str, Enum):
    STUDENT = "student"
    TEACHER = "teacher"

class User(TimeStampedModel, table=True):
    id_prefix: ClassVar[str] = "usr"

    tg_handle: str = Field(unique=True, index=True)
    telegram_id: str = Field(unique=True, index=True)  # Numeric Telegram ID

    role: UserRole
    meta: Dict = Field(default_factory=dict, sa_type=JSON)

    class Config:
        from_attributes = True
