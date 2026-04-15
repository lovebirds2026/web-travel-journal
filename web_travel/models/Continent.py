from sqlalchemy import Index, UniqueConstraint, Enum as saEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, FieldStatus

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
        saEnum(FieldStatus, name='status_enum', values_callable=lambda x: [e.value for e in x]), 
        default=FieldStatus.NEW)
    # note: this can be moved to Base's type_annotation_map if reuse needed ~
    # Status: sqlalchemy.Enum(FieldStatus, name='status_enum')
    countries: Mapped[list['Country']] = relationship(back_populates='continent')
    


