import requests

from sqlalchemy import create_engine, MetaData, Table, select, delete, bindparam, func
from sqlalchemy.dialects.postgresql import insert
from instance.config import Config
from web_travel.models import FieldStatus

countries = dict()
continents = set()

def get_country_data():
    response = requests.get('https://restcountries.com/v3.1/all?fields=name,continents')

    for country in response.json():
        countries[country['name']['common']] = country['continents']
        continents.update(country['continents'])

def update_db():
    engine = create_engine(Config.SQLALCHEMY_DATABASE_URI, echo=False)
    metadata_obj = MetaData()

    t_continent = Table('continent', metadata_obj, autoload_with=engine) # basic reflection
    t_country = Table('country', metadata_obj, autoload_with=engine)

    with engine.begin() as cursor:
        # update continents
        result = cursor.execute(select(t_continent.c.id, t_continent.c.name).order_by(t_continent.c.id)).all()
        db_continents = {r[1]: r[0] for r in result}
        for continent in continents:
            if continent not in db_continents:
                print(f'{continent} missing, will add.')
                result = cursor.execute(insert(t_continent).values(name=continent, status=FieldStatus.ACTIVE))
                db_continents.update({continent: result.inserted_primary_key[0]})

        # bulk insert countries with on conflict do nothing (PostgreSQL only)
        scalar_subq = (select(t_continent.c.id).where(t_continent.c.name == bindparam('continent'))
            .scalar_subquery()) # could use db_continents[], but this is fancy
        cursor.execute(insert(t_country).values(continentFK=scalar_subq, status=FieldStatus.NEW)
            .on_conflict_do_nothing(index_elements=[t_country.c.name]), 
            [{'name': key, 'continent': values[0]} for key, values in countries.items()])
        # NB: using the first continent from n here, e.g. for Turkey it's Europe (sorted)

        db_countries = cursor.execute(select(func.count()).select_from(t_country)).scalar()
        print(f'Total of {db_countries} countries in the database.')


if __name__ == '__main__':
    # for testing
    # continents = {'North America', 'Europe', 'Asia', 'South America', 'Oceania', 'Africa', 'Antarctica'}
    # countries = { 'Afghanistan': ['Asia'], 'Albania': ['Europe', 'Asia'], 'Italy': ['Antarctica'], }

    get_country_data()
    update_db()
