from sqlalchemy import Index, UniqueConstraint, Enum as saEnum, ForeignKey
from sqlalchemy.orm import Mapped, mapped_column, relationship

from . import Base, FieldStatus

class Country(Base):
    __tablename__ = 'country'
    __table_args__ = (
        # UniqueConstraint('name', name='U_name'),
        # Index('IDX_status', 'status'),
        {'extend_existing': True, },
    )

    _searchable_fields = ('id', 'name', )

    name: Mapped[str] = mapped_column(unique=True)
    status: Mapped[FieldStatus] = mapped_column(
        saEnum(FieldStatus, name='status_enum', values_callable=lambda x: [e.value for e in x]), 
        default=FieldStatus.NEW, index=True)
    continentFK: Mapped[int] = mapped_column(ForeignKey('continent.id'), nullable=True)
    continent: Mapped['Continent'] = relationship(back_populates='countries')
    


