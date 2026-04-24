from sqlalchemy import Index, ForeignKey, sql
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import date
from collections import defaultdict

from .. import db
from . import Base
from .Continent import Continent
from .Country import Country
from .Place import Place

class Travel(Base):
    __tablename__ = 'travel'
    __table_args__ = (
        Index('IDX_from_to', 'date_from', 'date_to'),
        {'extend_existing': True, },
    )

    _searchable_fields = ('title', )

    title: Mapped[str] = mapped_column(index=True) # may need to change this to "name"
    description: Mapped[str]
    user_note: Mapped[str]
    date_from: Mapped[date]
    date_to: Mapped[date]
    public: Mapped[bool] = mapped_column(server_default=sql.false(), index=True)
    ownerFK: Mapped[int] = mapped_column('owner_userFK', ForeignKey('user.id'))
    
    owner: Mapped['User'] = relationship(back_populates='travels')
    relations: Mapped[list['TravelRelation']] = relationship(back_populates='travel')
    

    def get_relation_names(self) -> dict[str, dict[int, str | None]]:
        buckets: dict[str, dict[int, str]] = defaultdict(dict) # {'country': {1: 'Italy', 2: 'Brazil'}, ..}
        for tr in self.relations:
            buckets[tr.relation][tr.relationFK] = None # will be the name

        model_map = {'continent': Continent, 'country': Country, 'place': Place}
        for rel, ids_vals in buckets.items():
            Model = model_map[rel]
            stmt = db.select(Model.id, Model.name).where(Model.id.in_(ids_vals.keys())).order_by(Model.name)
            rows = db.session.execute(stmt).all()
            buckets[rel] = {} # clear the dict to insert sorted names
            for row_id, row_name in rows:
                buckets[rel][row_id] = row_name

        return dict(buckets)

