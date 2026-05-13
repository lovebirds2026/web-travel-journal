from sqlalchemy import UniqueConstraint, Index, String, sql, Enum as saEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import db
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


    @classmethod
    def get_from_relation(cls, relation: Base, limit=100):
        """ Returns all photos for a given object (continent/country/place/travel). """
        tablename = relation.__tablename__
        stmt = (db.select(cls).select_from(PhotoRelation)
            .where(PhotoRelation.relation == tablename, PhotoRelation.relationFK == relation.id)
            .join(cls, cls.id == PhotoRelation.photoFK)
            .order_by(cls.id.asc())
            .limit(limit)
        )
        photos = db.session.scalars(stmt).all()
        return photos
