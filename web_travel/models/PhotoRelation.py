from sqlalchemy import Index, UniqueConstraint, ForeignKey, Enum as saEnum, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from collections import namedtuple
Card = namedtuple('Card', ('name', 'type', 'id', 'img'))

from .. import db
from .Continent import Continent, FieldStatus
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
        """ All possible relations for attaching to a photo """
        if not exclude:
            exclude = {}
        return {
            'continent': {c.id: c.name for c in Continent.get_active() if not exclude.get('continent', {}).get(c.id)},
            'country': {c.id: c.name for c in Country.get_active() if not exclude.get('country', {}).get(c.id)},
            'place': {p.id: p.name for p in Place.get_active() if not exclude.get('place', {}).get(p.id)},
            'travel': {t.id: t.title for t in Travel.get_own(user_id, admin) 
                                    if not exclude.get('travel', {}).get(t.id)},
        }

    @classmethod
    def get_card_data(cls, Relation, ids_list=None, last=True, limit=50):
        from .Photo import Photo # deferred import to avoid circular

        # get the last photo relation for each id of this type (changes up the site)
        conditions_subq = [cls.relation == Relation.__tablename__]
        if ids_list is not None:
            conditions_subq.append(cls.relationFK.in_(ids_list))
        aggregatorfn = func.max if last else func.min

        latest_sq = (db.select(cls.relation, cls.relationFK, aggregatorfn(cls.photoFK).label('photo_id'))
            .where(*conditions_subq)
            .group_by(cls.relation, cls.relationFK)
            .limit(limit)
            .subquery()
        )

        # join to get the photo path and the relation name
        conditions_main = [Relation.deleted == False]
        if name_col := getattr(Relation, 'name', False):
            # Continent/Country/Place
            conditions_main.append(Relation.status == FieldStatus.ACTIVE)
        else:
            # Travel
            name_col = Relation.title
            conditions_main.append(Relation.public == True)

        stmt = (db.select(name_col, latest_sq.c.relation, latest_sq.c.relationFK,
            func.concat(Photo.filename, '.', Photo.extension))
            .join(Photo, Photo.id == latest_sq.c.photo_id)
            .join(Relation, Relation.id == latest_sq.c.relationFK)
            .where(*conditions_main)
        )
        latest_photo_relations = db.session.execute(stmt).all()
        return [Card(*row) for row in latest_photo_relations]