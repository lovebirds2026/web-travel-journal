# this file must be here to make this a module
from sqlalchemy import func, DateTime
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime

from .. import db

class Base(db.Model):
    __abstract__ = True

    _searchable_fields = NotImplemented

    # fields
    id: Mapped[int] = mapped_column(primary_key=True, sort_order=-1)
    cid: Mapped[int] = mapped_column(nullable=True)
    ct: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    uid: Mapped[int] = mapped_column(nullable=True)
    ut: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=func.now(), onupdate=func.now())
    deleted: Mapped[bool]


    @classmethod
    def search_and_filter(cls, filters, search_field=None, search_text=None):
        stmt = db.select(cls).filter_by(**filters)
        if search_text and search_field and search_field in cls._searchable_fields:
            field = getattr(cls, search_field)
            stmt = stmt.where(field.icontains(search_text))
        return stmt.order_by(cls.id.asc())