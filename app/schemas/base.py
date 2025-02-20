from datetime import datetime
from typing import Optional, Dict
from sqlmodel import SQLModel, Field
from uuid import uuid4
from enum import Enum
from sqlalchemy import JSON

class Status(str, Enum):
    COMPLETED = "completed"
    PENDING = "pending"
    CANCELLED = "cancelled"

class TimeStampedModel(SQLModel):
    id: str = Field(default=None, primary_key=True)
    created_at: datetime = Field(
        default_factory=datetime.utcnow,
        nullable=False
    )

    def __init__(self, **data):
        if 'id' not in data:
            prefix = getattr(self, 'id_prefix', 'item')
            data['id'] = f"{prefix}_{uuid4()}"
        super().__init__(**data)

class SequenceItemBase(TimeStampedModel):
    # previous_id: Optional[str] = Field(default=None)
    content: Dict = Field(default_factory=dict, sa_type=JSON)
    status: Status = Field(default=Status.PENDING)
