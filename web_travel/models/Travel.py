from sqlalchemy import Index, ForeignKey, sql, update
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import date
from collections import defaultdict

from .. import db
from . import Base
from .Continent import Continent
from .Country import Country
from .Place import Place
from .TravelRelation import TravelRelation

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
    
    owner: Mapped['User'] = relationship(back_populates='travels')
    relations: Mapped[list['TravelRelation']] = relationship(back_populates='travel', cascade='all, delete-orphan')
    

    @classmethod
    def validate_input(cls, form: dict) -> list:
        errors = []
        title = form.get('title')
        date_from = form.get('date_from')
        date_to = form.get('date_to')
        if not title:
            errors.append('Travel name is required.')
        if not date_from or not date_to:
            errors.append('Both from and to dates are required.')
        else:
            try:
                date_from = date.fromisoformat(date_from)
                date_to = date.fromisoformat(date_to)
            except ValueError:
                errors.append('Invalid date format.')

        return errors


    @classmethod
    def add_edit(cls, form: dict):
        date_from = date.fromisoformat(form.get('date_from'))
        date_to = date.fromisoformat(form.get('date_to'))
        values_dict = dict(
            title=form.get('title'),
            description=form.get('description', ''),
            user_note=form.get('notes', ''),
            date_from=date_from,
            date_to=date_to,
            public=bool(form.get('public', False)),
        )
        if travel_id := form.get('id', 0): # Update
            stmt = update(cls).where(cls.id == travel_id).values(values_dict)
            db.session.execute(stmt)
            travel = db.session.get(cls, travel_id)
        else: # Add
            new_travel = cls(**values_dict)
            db.session.add(new_travel)
            travel = new_travel

        relations = form.getlist('relations[]') # ['continent:2', 'country:3', ]
        travel.update_relations(relations)

        db.session.commit()


    def update_relations(self, relations):
        submitted = {tuple(rel.split(':')) for rel in relations}
        existing = {(tr.relation, str(tr.relationFK)) for tr in self.relations}
        # add
        for rel_type, rel_id in submitted - existing:
            self.relations.append(TravelRelation(relation=rel_type, relationFK=int(rel_id)))
        # remove
        for tr in list(self.relations):
            if(tr.relation, str(tr.relationFK)) not in submitted:
                self.relations.remove(tr)


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
