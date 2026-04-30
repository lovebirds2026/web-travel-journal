from sqlalchemy import UniqueConstraint, Index, String, sql, Enum as saEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, FieldStatus, HasRelationsMixin
from .PhotoRelation import PhotoRelation

class Photo(HasRelationsMixin, Base):
    __tablename__ = 'photo'
    __table_args__ = (
        UniqueConstraint('filename', 'extension', name='U_filename_extension'),
        Index('IDX_status_public', 'status', 'public'),
        {'extend_existing': True, },
    )

    _searchable_fields = ('filename', )

    filename: Mapped[str]
    extension: Mapped[str] = mapped_column(String(5))
    size: Mapped[int]
    label: Mapped[str] = mapped_column(server_default='')
    description: Mapped[str] = mapped_column(server_default='')
    public: Mapped[bool] = mapped_column(server_default=sql.false())
    status: Mapped[FieldStatus] = mapped_column(
        saEnum(FieldStatus, name='status_enum', values_callable=lambda x: [e.value for e in x]), 
        default=FieldStatus.NEW)

    owner: Mapped['User'] = relationship(back_populates='photos')
    relations: Mapped[list['PhotoRelation']] = relationship(back_populates='photo', cascade='all, delete-orphan')


