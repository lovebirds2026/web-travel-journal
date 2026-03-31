from sqlalchemy import Index, UniqueConstraint
from sqlalchemy.orm import Mapped, mapped_column

from typing import Optional
from enum import StrEnum

from . import Base

class FieldStatus(StrEnum):
    NEW = 'new'
    REJECTED = 'rejected'
    ACTIVE = 'active'

class Continent(Base):
    __tablename__ = 'continent'
    __table_args__ = (
        UniqueConstraint('name', name="U_name"),
        Index('IDX_status', 'status'),
        {'keep_existing': True, },
    )
     # or extend_existing

    name: Mapped[str]
    status: Mapped[str] = mapped_column(default='new')


    


