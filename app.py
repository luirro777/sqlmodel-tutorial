from sqlmodel import Field, SQLModel, create_engine, Session, select, col, or_

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    #name: str = Field(index=True)
    secret_name: str
    age: int | None = None

sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

engine = create_engine(sqlite_url, echo=True)

def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
    hero_4 = Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32)
    hero_5 = Hero(name="Black Lion", secret_name="Trevor Challa", age=35)
    hero_6 = Hero(name="Dr. Weird", secret_name="Steve Weird", age=36)
    hero_7 = Hero(name="Captain North America", secret_name="Esteban Rogelios", age=93)
    '''
    session = Session(engine)

    session.add(hero_1)
    session.add(hero_2)
    session.add(hero_3)
    session.add(hero_4)
    session.add(hero_5)
    session.add(hero_6)
    session.add(hero_7)

    session.commit()

    session.close()
    '''
    with Session(engine) as session:
        session.add(hero_1)
        session.add(hero_2)
        session.add(hero_3)
        session.add(hero_4)
        session.add(hero_5)
        session.add(hero_6)
        session.add(hero_7)
        
        session.commit()

def select_heroes():
    with Session(engine) as session:
        '''
            SELECT id, name, secret_name, age
            FROM hero
        '''
        statement = select(Hero)
        results = session.exec(statement)
        #primer manera:
        #for h in results:
        #    print(h)

        #segunda manera:
        #heroes = results.all()

        #tercer manera (resumida)
        #heroes = session.exec(select(Hero)).all()

        #con where
        #statement_where = select(Hero).where(Hero.name == "Deadpond")
        #statement_where = select(Hero).where(Hero.age > 35)
        #statement_where = select(Hero).where(col(Hero.name).in_(["Deadpond", "Ratman"]))
        #statement_where = select(Hero).where(Hero.age >= 35, Hero.age < 40)
        statement_where = select(Hero).where(or_(Hero.age <= 35, Hero.age > 90))
        results = session.exec(statement_where)
        for h in results:
            print(h)
        #para imprimir solo el primero:
        #hero = results.first()
        #print("Hero:", hero)

def main():
    create_db_and_tables()
    create_heroes()
    select_heroes()




if __name__ == "__main__":
    main()