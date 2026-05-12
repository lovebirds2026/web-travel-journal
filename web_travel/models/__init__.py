from flask import session
from sqlalchemy import ForeignKey, sql, func, DateTime, cast, String, inspect
from sqlalchemy.orm import Mapped, mapped_column

from datetime import datetime, UTC
from enum import StrEnum
from collections import defaultdict

from .. import db

class FieldStatus(StrEnum):
    NEW = 'new'
    ACTIVE = 'active'
    REJECTED = 'rejected'

class Base(db.Model):
    __abstract__ = True

    _searchable_fields = NotImplemented

    _POLYMORPHIC_MODEL_MAP = {}

    # fields
    id: Mapped[int] = mapped_column(primary_key=True, sort_order=-1)
    cid: Mapped[int] = mapped_column(ForeignKey('user.id'), nullable=True, default=lambda: session.get('user_id'))
    ct: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    uid: Mapped[int] = mapped_column(nullable=True, onupdate=lambda: session.get('user_id'))
    ut: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), 
        onupdate=lambda: datetime.now(UTC))
    deleted: Mapped[bool] = mapped_column(server_default=sql.false())


    def get_thumbnail(self) -> tuple[str, str] | None: # @TODO: check if it gets cached
        from .Photo import Photo
        from .PhotoRelation import PhotoRelation
        print(f'Getting thumbnail for {type(self).__tablename__} {self.id}')
        scalar_subq = (db.select(PhotoRelation.photoFK)
            .where(PhotoRelation.relation == type(self).__tablename__, PhotoRelation.relationFK == self.id)
            .order_by(PhotoRelation.photoFK.desc()).limit(1).scalar_subquery())
        photo = db.session.execute(
            db.select(func.concat(Photo.filename, '.', Photo.extension)).where(Photo.id == scalar_subq)
        ).scalar()
        return photo

    @classmethod
    def search_and_filter(cls, filters, search_field=None, search_text=None):
        stmt = db.select(cls).filter_by(**filters)
        if search_text and search_field and search_field in cls._searchable_fields:
            field = cast(getattr(cls, search_field), String) # just to practice cast(), not cool with id
            stmt = stmt.where(field.icontains(search_text))
        return stmt.order_by(cls.id.asc())

    @classmethod
    def get_active(cls): # Note: won't work for all tables, consider Mixin
        stmt = db.select(cls).where(
            cls.deleted == False, cls.status == FieldStatus.ACTIVE
        ).order_by(cls.name.asc())
        return db.session.scalars(stmt).all()

    @classmethod
    def get_model_class(cls, tablename: str):
        if not Base._POLYMORPHIC_MODEL_MAP:
            # populate class attribute (once)
            for mapper in db.Model.registry.mappers:
                if t_name := getattr(mapper.class_, '__tablename__', False):
                    Base._POLYMORPHIC_MODEL_MAP[t_name] = mapper.class_
        return Base._POLYMORPHIC_MODEL_MAP[tablename]


class HasRelationsMixin:
    """ Adds useful methods for the 'relations' model attribute """

    def get_relation_names(self) -> dict[str, dict[int, str | None]]:
        buckets: dict[str, dict[int, str]] = defaultdict(dict) # {'country': {1: 'Italy', 2: 'Brazil'}, ..}
        for tr in self.relations:
            buckets[tr.relation][tr.relationFK] = None # will be the name

        for rel, ids_vals in buckets.items():
            Model = self.get_model_class(rel)
            name_col = getattr(Model, 'name', False) or Model.title
            stmt = db.select(Model.id, name_col).where(Model.id.in_(ids_vals.keys())).order_by(name_col)
            rows = db.session.execute(stmt).all()
            buckets[rel] = {} # clear the dict to insert sorted names
            for row_id, row_name in rows:
                buckets[rel][row_id] = row_name

        return dict(buckets)


    def update_relations(self, relations):
        mapper = inspect(type(self))
        RelationClass = mapper.relationships['relations'].mapper.class_

        submitted = {tuple(rel.split(':')) for rel in relations}
        existing = {(tr.relation, str(tr.relationFK)) for tr in self.relations}
        # add
        for rel_type, rel_id in submitted - existing:
            self.relations.append(RelationClass(relation=rel_type, relationFK=int(rel_id)))
        # remove
        for tr in list(self.relations):
            if(tr.relation, str(tr.relationFK)) not in submitted:
                self.relations.remove(tr)

