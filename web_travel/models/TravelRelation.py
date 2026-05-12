from sqlalchemy import Index, UniqueConstraint, ForeignKey, Enum as saEnum
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import db
from .Continent import Continent
from .Country import Country
from .Place import Place

class TravelRelation(db.Model): # no need to get the default fields.. I think.
    __tablename__ = 'travel_relation'
    __table_args__ = (
        UniqueConstraint('travelFK', 'relation', 'relationFK', name='U_travelFK_relation_relationFK'),
        Index('IDX_relation_relationFK', 'relation', 'relationFK'),
        {'extend_existing': True, },
    )

    id: Mapped[int] = mapped_column(primary_key=True)
    travelFK: Mapped[int] = mapped_column('travelFK', ForeignKey('travel.id'))
    relation: Mapped[str] = mapped_column(saEnum(
        'continent', 'country', 'place',
        name='relation_t_enum',
        validate_strings=True,
        create_constraint=True,
        native_enum=False
    ))
    relationFK: Mapped[int]
    travel: Mapped['Travel'] = relationship(back_populates='relations')


    @classmethod
    def as_dict(cls, exclude: dict=None):
        """ All possible relations for attaching to a travel """
        if not exclude:
            exclude = {}
        return {
            'continent': {c.id: c.name for c in Continent.get_active() if not exclude.get('continent', {}).get(c.id)},
            'country': {c.id: c.name for c in Country.get_active() if not exclude.get('country', {}).get(c.id)},
            'place': {p.id: p.name for p in Place.get_active() if not exclude.get('place', {}).get(p.id)},
        }