from sqlalchemy import Index, UniqueConstraint, Enum as saEnum
from sqlalchemy.orm import Mapped, mapped_column

from typing import Optional
from enum import StrEnum

from . import Base

class FieldStatus(StrEnum):
    NEW = 'new'
    ACTIVE = 'active'
    REJECTED = 'rejected'

class Continent(Base):
    __tablename__ = 'continent'
    __table_args__ = (
        UniqueConstraint('name', name='U_name'),
        Index('IDX_status', 'status'),
        {'extend_existing': True, },
    )

    _searchable_fields = ('id', 'name', )

    name: Mapped[str]
    status: Mapped[FieldStatus] = mapped_column(
        saEnum(FieldStatus, name='continent_status_enum', values_callable=lambda x: [e.value for e in x]), 
        default=FieldStatus.NEW)
    # note: this can be moved to Base's type_annotation_map if reuse needed ~
    # Status: sqlalchemy.Enum(FieldStatus, name='status_enum')

    


