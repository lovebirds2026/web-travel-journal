from sqlalchemy import Index, ForeignKey, sql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import date

from . import Base

class Travel(Base):
    __tablename__ = 'travel'
    __table_args__ = (
        Index('IDX_from_to', 'date_from', 'date_to'),
        {'extend_existing': True, },
    )

    _searchable_fields = ('title', )

    title: Mapped[str] = mapped_column(index=True)
    user_note: Mapped[str]
    date_from: Mapped[date]
    date_to: Mapped[date]
    public: Mapped[bool] = mapped_column(server_default=sql.false(), index=True)
    ownerFK: Mapped[int] = mapped_column('owner_userFK', ForeignKey('user.id'))
    
    owner: Mapped['User'] = relationship(back_populates='travels')
    


