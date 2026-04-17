from sqlalchemy import Index, UniqueConstraint, Enum as saEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

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
    ownerFK: Mapped[int] = mapped_column('owner_userFK', ForeignKey('user.id'))
    
    country: Mapped['Country'] = relationship(back_populates='places')
    owner: Mapped['User'] = relationship(back_populates='places')
    


