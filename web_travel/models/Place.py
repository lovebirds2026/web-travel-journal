from sqlalchemy import Enum as saEnum, ForeignKey, update
from sqlalchemy.orm import Mapped, mapped_column, relationship

from .. import db
from . import Base, FieldStatus

class Place(Base):
    __tablename__ = 'place'
    __table_args__ = (
        {'extend_existing': True, },
    )

    _searchable_fields = ('name', 'description', )

    name: Mapped[str]
    description: Mapped[str]
    status: Mapped[FieldStatus] = mapped_column(
        saEnum(FieldStatus, name='status_enum', values_callable=lambda x: [e.value for e in x]), 
        default=FieldStatus.NEW, index=True)
    countryFK: Mapped[int] = mapped_column(ForeignKey('country.id'), nullable=True)
    
    country: Mapped['Country'] = relationship(back_populates='places')
    owner: Mapped['User'] = relationship(back_populates='places')
    

    @classmethod
    def add_edit(cls, form: dict, is_admin=False) -> list:
        errors = []
        name = form.get('name')
        country_id = form.get('country_id')
        if not name:
            errors.append('Invalid place name.')
        if not country_id:
            errors.append('Please assign a country.')
        if errors:
            return errors

        # Proceed updating/creating
        values_dict = dict(
            name=name,
            description=form.get('description', ''),
            countryFK=country_id,
            deleted=bool(form.get('deleted')),
        )
        if is_admin and form.get('status'):
            values_dict['status'] = form.get('status')

        if place_id := form.get('id', 0): # Update
            stmt = update(cls).where(cls.id == place_id).values(values_dict)
            db.session.execute(stmt)
        else: # Add
            new_place = cls(**values_dict)
            db.session.add(new_place)

        db.session.commit()