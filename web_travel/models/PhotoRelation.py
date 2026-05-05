from sqlalchemy import Index, UniqueConstraint, ForeignKey, Enum as saEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import db
from .Continent import Continent
from .Country import Country
from .Place import Place
from .Travel import Travel

class PhotoRelation(db.Model):
    __tablename__ = 'photo_relation'
    __table_args__ = (
        UniqueConstraint('photoFK', 'relation', 'relationFK', name='U_photoFK_relation_relationFK'),
        Index('IDX_photorelation_relationFK', 'relation', 'relationFK'),
        {'extend_existing': True, },
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    photoFK: Mapped[int] = mapped_column('photoFK', ForeignKey('photo.id'))
    relation: Mapped[str] = mapped_column(saEnum(
        'continent', 'country', 'place', 'travel',
        name='relation_p_enum',
        validate_strings=True,
        create_constraint=True,
        native_enum=False
    ))
    relationFK: Mapped[int]
    photo: Mapped['Photo'] = relationship(back_populates='relations')


    @classmethod
    def as_dict(cls, user_id, admin=False, exclude: dict=None):
        if not exclude:
            exclude = {}
        return {
            'continent': {c.id: c.name for c in Continent.get_active() if not exclude.get('continent', {}).get(c.id)},
            'country': {c.id: c.name for c in Country.get_active() if not exclude.get('country', {}).get(c.id)},
            'place': {p.id: p.name for p in Place.get_active() if not exclude.get('place', {}).get(p.id)},
            'travel': {t.id: t.title for t in Travel.get_own(user_id, admin) 
                                    if not exclude.get('travel', {}).get(t.id)},
        }