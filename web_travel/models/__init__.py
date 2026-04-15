# this file must be here to make this a module
from sqlalchemy import sql, func, DateTime, cast, String
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, UTC
from enum import StrEnum

from .. import db

class FieldStatus(StrEnum):
    NEW = 'new'
    ACTIVE = 'active'
    REJECTED = 'rejected'

class Base(db.Model):
    __abstract__ = True

    _searchable_fields = NotImplemented

    # fields
    id: Mapped[int] = mapped_column(primary_key=True, sort_order=-1)
    cid: Mapped[int] = mapped_column(nullable=True)
    ct: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    uid: Mapped[int] = mapped_column(nullable=True)
    ut: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), 
        onupdate=lambda: datetime.now(UTC))
    deleted: Mapped[bool] = mapped_column(server_default=sql.false())


    @classmethod
    def search_and_filter(cls, filters, search_field=None, search_text=None):
        stmt = db.select(cls).filter_by(**filters)
        if search_text and search_field and search_field in cls._searchable_fields:
            field = cast(getattr(cls, search_field), String) # just to practice cast(), not cool with id
            stmt = stmt.where(field.icontains(search_text))
        return stmt.order_by(cls.id.asc())
