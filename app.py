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
'''
A partir de aquí:

CRUD:
- C -> CREATE -> create_heroes()
- R -> READ -> select_heroes()
- U -> UPDATE -> update_heroes()
- D -> DELETE -> delete_heroes()

'''

def create_heroes():
    hero_1 = Hero(name="Deadpond", secret_name="Dive Wilson")
    hero_2 = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")
    hero_3 = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
    hero_4 = Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32)
    hero_5 = Hero(name="Black Lion", secret_name="Trevor Challa", age=35)
    hero_6 = Hero(name="Dr. Weird", secret_name="Steve Weird", age=36)
    hero_7 = Hero(name="Captain North America", secret_name="Esteban Rogelios", age=93)
    '''
    #Podriamos hacerlo asi:

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

    #Pero es mucho más práctico y recomendable hacerlo de esta manera:
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
        #statement = select(Hero)
        #results = session.exec(statement)
        #primer manera:
        #for h in results:
        #    print(h)

        #segunda manera:
        #heroes = results.all()

        #tercer manera (resumida)
        #heroes = session.exec(select(Hero)).all()

        #con where
        #statement = select(Hero).where(Hero.name == "Deadpond")
        #statement = select(Hero).where(Hero.age > 35)
        #statement = select(Hero).where(col(Hero.name).in_(["Deadpond", "Ratman"]))
        #statement = select(Hero).where(Hero.age >= 35, Hero.age < 40)
        #statement = select(Hero).where(or_(Hero.age <= 35, Hero.age > 90))
        #results = session.exec(statement)
        #for h in results:
        #    print(h)

        #para imprimir solo el primero:
        #hero = results.first()
        #print("Hero:", hero)

        #Para imprimir el primero y asegurarnos que solo exista un solo resultado
        #hero = results.one()
        #print("Hero:", hero)

        #Seleccionar por id
        #hero = session.get(Hero, 1)
        #print("Hero:", hero)

        #Limitar a 3 resultados
        #statement = select(Hero).limit(3)
        #results = session.exec(statement)
        #heroes = results.all()
        #print(heroes)

        #Si queremos navegar hacia los proximos 3 resultados, debemos usar offset
        #statement = select(Hero).offset(3).limit(3)
        #results = session.exec(statement)
        #heroes = results.all()
        #print(heroes)

        #... y una vez más para cubrir la totalidad (3 + 3 = 6)
        #statement = select(Hero).offset(6).limit(3)
        #results = session.exec(statement)
        #heroes = results.all()
        #print(heroes)

def update_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Boy")
        results = session.exec(statement)
        hero = results.one()
        print("Hero:", hero)

        hero.age = 16
        session.add(hero)
        session.commit()
        session.refresh(hero)
        print("Updated hero:", hero)

def delete_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Youngster")
        results = session.exec(statement)
        hero = results.one()
        print("Hero: ", hero)

        session.delete(hero)
        session.commit()

        print("Deleted hero:", hero)

        statement = select(Hero).where(Hero.name == "Spider-Youngster")
        results = session.exec(statement)
        hero = results.first()

        if hero is None:
            print("There's no hero named Spider-Youngster")

def main():
    create_db_and_tables()
    create_heroes()
    select_heroes()
    update_heroes()
    delete_heroes()





if __name__ == "__main__":
    main()