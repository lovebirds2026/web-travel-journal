from sqlalchemy import Index, sql, update
from sqlalchemy.orm import Mapped, mapped_column, relationship

from datetime import date

from .. import db
from . import Base, HasRelationsMixin
from .TravelRelation import TravelRelation

class Travel(HasRelationsMixin, Base):
    __tablename__ = 'travel'
    __table_args__ = (
        Index('IDX_from_to', 'date_from', 'date_to'),
        {'extend_existing': True, },
    )

    _searchable_fields = ('title', 'description', 'user_note', )

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


    @classmethod
    def get_own(cls, user_id, admin=False):
        stmt = db.select(Travel).where(Travel.deleted == False).order_by(Travel.title.asc())
        if not admin:
            stmt = stmt.where(Travel.cid == user_id)
        return db.session.scalars(stmt).all()

