from sqlmodel import Field, SQLModel, create_engine, Session, select, col, or_

class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)    
    name: str = Field(index=True)
    secret_name: str
    age: int | None = None
    team_id: int | None = Field(default=None, foreign_key="team.id")

class Gadget(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key= True)
    name: str = Field(index=True)
    hero_id : int | None = Field(default=None, foreign_key = "hero.id")



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
    
        
    with Session(engine) as session:

        # Creamos teams
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")

        # Escribimos los teams en la BD
        session.add(team_preventers)
        session.add(team_z_force)
        session.commit()
    
        # Creamos heroes
        hero_deadpond = Hero(
                name="Deadpond", 
                secret_name="Dive Wilson", 
                team_id=team_z_force.id
        )
        hero_rusty_man = Hero(
                name="Rusty-Man",
                secret_name="Tommy Sharp",
                age=48,
                team_id=team_preventers.id,
        )
        hero_spider_boy = Hero(
                name="Spider-Boy", 
                secret_name="Pedro Parqueador"
        )
    
        # .. y tambien los escribimos
        session.add(hero_deadpond)
        session.add(hero_rusty_man)
        session.add(hero_spider_boy)     
        session.commit()

        # ... e imprimimos por pantalla
        session.refresh(hero_deadpond)
        session.refresh(hero_rusty_man)
        session.refresh(hero_spider_boy)

        print("Created hero:", hero_deadpond)
        print("Created hero:", hero_rusty_man)
        print("Created hero:", hero_spider_boy)

def create_gadgets():
    with Session(engine) as session:
        rusty = session.exec(select(Hero).where(Hero.name == "Rusty-Man")).one()
        spider = session.exec(select(Hero).where(Hero.name == "Spider-Boy")).one()

        g1 = Gadget(name="Escudo de Vibranium", hero_id=rusty.id)
        g2 = Gadget(name="Lanza-telarañas", hero_id=spider.id)

        session.add(g1)
        session.add(g2)
        session.commit()
        session.refresh(g1)
        session.refresh(g2)
        print("Gadget 1:", g1)
        print("Gadget 2:", g2)
        
def find_specific_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(
            or_(
                Hero.age > 40,
                col(Hero.name).in_(["Spider-Boy", "Deadpond"])
            )
        )
        heroes = session.exec(statement).all()
        for hero in heroes:
            print("Heroe encontrado: ", hero)

def get_heroes_and_headquarters():
    with Session(engine) as session:
        statement = select(Hero, Team).join(Team)
        results = session.exec(statement)
        for hero, team in results:
            print(f"El héroe {hero.name} opera desde el cuartel {team.headquarters}")

def paginate_heroes(page: int, page_size: int = 2):
    offset_value = (page - 1) * page_size
    with Session(engine) as session:
        statement = select(Hero).offset(offset_value).limit(page_size)
        heroes = session.exec(statement).all()
        print(f"--- Pagina {page} ----")
        for hero in heroes:
            print(hero)

def transfer_or_reassign_hero():
    with Session(engine) as session:
        hero = session.exec(select(Hero).where(Hero.name == "Deadpond")).one()
        preventers = session.exec(select(Team).where(Team.name == "Preventers")).one()

        hero.team_id = preventers.id
        session.add(hero)
        session.commit()
        session.refresh(hero)

        print(f"{hero.name} ahora pertenece a {hero.team_id}")

def select_heroes():
    with Session(engine) as session:

        # JOIN (con where)
        #statement = select(Hero, Team).where(Hero.team_id == Team.id)
        #results = session.exec(statement)
        #for hero, team in results:
        #    print("Hero:", hero, "Team:", team)

        # JOIN con Join
        #statement = select(Hero, Team).join(Team)
        #results = session.exec(statement)
        #for hero, team in results:
        #    print("Hero:", hero, "Team:", team)

        # left outer join
        #statement = select(Hero, Team).join(Team, isouter=True)
        #results = session.exec(statement)
        #for hero, team in results:
        #    print("Hero:", hero, "Team:", team)

        # Y si solo metemos info de Hero? (podemos incluso usar un where despues ;) )
        statement = select(Hero).join(Team).where(Team.name == "Preventers")
        results = session.exec(statement)
        for hero in results:
            print("Preventer Hero:", hero)


        
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

        team_statement = select(Team).where(Team.name == "Preventers")
        team = session.exec(team_statement).one()

        hero.age = 16
        hero.team_id = team.id

        session.add(hero)
        session.commit()
        session.refresh(hero)
        print("Updated hero:", hero)

def break_connection():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Boy")
        results = session.exec(statement)
        hero = results.one()
        print("Hero:", hero)

        hero.team_id = None

        session.add(hero)
        session.commit()
        session.refresh(hero)
        print("No es mas preventer:", hero)
    

def delete_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Boy")
        results = session.exec(statement)
        hero = results.one()
        print("Hero: ", hero)

        session.delete(hero)
        session.commit()

        print("Deleted hero:", hero)

        statement = select(Hero).where(Hero.name == "Spider-Boy")
        results = session.exec(statement)
        hero = results.first()

        if hero is None:
            print("There's no hero named Spider-Boy")

def main():
    create_db_and_tables()
    create_heroes()
    create_gadgets()
    find_specific_heroes()
    get_heroes_and_headquarters()
    paginate_heroes(2)
    transfer_or_reassign_hero()
    #select_heroes()
    #update_heroes()
    #break_connection()
    #delete_heroes()





if __name__ == "__main__":
    main()