"""
01 - ATRIBUTOS DE RELACIÓN EN SQLMODEL: CRUD completo
======================================================

Cubre, en un solo flujo ejecutable:
  - Define Relationship Attributes
  - Create and Update Relationships
  - Read Relationships
  - Remove Relationships
  - Relationship back_populates

Ejecutar:  python 01_relaciones_crud.py
Cada corrida borra y recrea la base sqlite para que el resultado sea
siempre el mismo (útil para mostrar en clase repetidas veces).
"""

import os
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select

# ---------------------------------------------------------------------------
# 1) DEFINE RELATIONSHIP ATTRIBUTES
# ---------------------------------------------------------------------------
# `team_id` es un campo PLANO: representa una columna real (una FK) en la tabla.
# `heroes` y `team` son "Relationship attributes": NO son columnas, son
# convenience attributes que SQLAlchemy resuelve por nosotros usando esa FK.
#
# - Team.heroes  -> list["Hero"]   (lado "muchos")
# - Hero.team    -> Team | None    (lado "uno", por eso puede ser None:
#                                   el team_id también puede ser NULL)


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    # back_populates="team" le dice a SQLAlchemy: "el otro lado de esta
    # relación es el atributo `team` en el modelo Hero". Así, cuando yo
    # modifico un lado (ej. hero.team = x), el otro lado (team.heroes)
    # se actualiza AUTOMÁTICAMENTE en memoria, sin necesitar un commit.
    heroes: list["Hero"] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    team_id: int | None = Field(default=None, foreign_key="team.id")
    team: Team | None = Relationship(back_populates="heroes")


sqlite_file_name = "relaciones_crud.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"

# echo=True para que los alumnos vean el SQL real que dispara cada operación
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


# ---------------------------------------------------------------------------
# 2) CREATE AND UPDATE RELATIONSHIPS
# ---------------------------------------------------------------------------
def create_heroes():
    with Session(engine) as session:
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")

        # --- Asignar el objeto Team completo (no el id) al crear un Hero ---
        # Ni team_preventers ni team_z_force tienen id todavía (no hicimos
        # commit), y no importa: SQLAlchemy los va a crear e ID-ar solos
        # cuando hagamos commit, porque están conectados a heroes que sí
        # vamos a agregar a la sesión.
        hero_deadpond = Hero(
            name="Deadpond", secret_name="Dive Wilson", team=team_z_force
        )
        hero_rusty_man = Hero(
            name="Rusty-Man", secret_name="Tommy Sharp", age=48, team=team_preventers
        )
        hero_spider_boy = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")

        # --- DEMO de back_populates, ANTES del commit ---
        # Como asignamos team=team_z_force en el constructor de Hero,
        # SQLAlchemy ya actualizó el otro lado de la relación en memoria:
        print("back_populates en memoria, antes de session.add():")
        print("  team_z_force.heroes contiene ya a Deadpond:", hero_deadpond in team_z_force.heroes)

        session.add(hero_deadpond)
        session.add(hero_rusty_man)
        session.add(hero_spider_boy)
        session.commit()  # 👈 un solo commit, no dos como con team_id=team.id

        session.refresh(hero_deadpond)
        session.refresh(hero_rusty_man)
        session.refresh(hero_spider_boy)

        print("Hero creado:", hero_deadpond)
        print("Hero creado:", hero_rusty_man)
        print("Hero creado:", hero_spider_boy)

        # --- Asignar una relación después de crear el objeto ---
        hero_spider_boy.team = team_preventers
        session.add(hero_spider_boy)
        session.commit()
        session.refresh(hero_spider_boy)
        print("Hero actualizado:", hero_spider_boy)

        # --- Crear un Team pasando directamente la lista de heroes ---
        hero_black_lion = Hero(name="Black Lion", secret_name="Trevor Challa", age=35)
        hero_sure_e = Hero(name="Princess Sure-E", secret_name="Sure-E")
        team_wakaland = Team(
            name="Wakaland",
            headquarters="Wakaland Capital City",
            heroes=[hero_black_lion, hero_sure_e],
        )
        session.add(team_wakaland)
        session.commit()
        session.refresh(team_wakaland)
        print("Team creado con heroes:", team_wakaland)

        # --- Conectar datos desde el lado "muchos": team.heroes.append(...) ---
        hero_tarantula = Hero(name="Tarantula", secret_name="Natalia Roman-on", age=32)
        hero_dr_weird = Hero(name="Dr. Weird", secret_name="Steve Weird", age=36)
        hero_cap = Hero(
            name="Captain North America", secret_name="Esteban Rogelios", age=93
        )

        team_preventers.heroes.append(hero_tarantula)
        team_preventers.heroes.append(hero_dr_weird)
        team_preventers.heroes.append(hero_cap)
        session.add(team_preventers)
        session.commit()
        session.refresh(hero_tarantula)
        session.refresh(hero_dr_weird)
        session.refresh(hero_cap)
        print("Preventers, hero nuevo:", hero_tarantula)
        print("Preventers, hero nuevo:", hero_dr_weird)
        print("Preventers, hero nuevo:", hero_cap)


# ---------------------------------------------------------------------------
# 3) READ RELATIONSHIPS
# ---------------------------------------------------------------------------
def select_heroes():
    with Session(engine) as session:
        # Leer del lado "uno a muchos": team.heroes es una lista de objetos
        # Hero completos, no una lista de ids.
        statement = select(Team).where(Team.name == "Preventers")
        team_preventers = session.exec(statement).one()
        print("Heroes de Preventers:", team_preventers.heroes)

        # Leer del lado "muchos a uno": hero.team es el objeto Team completo
        # (o None). Patrón típico: chequear primero si existe.
        statement = select(Hero).where(Hero.name == "Deadpond")
        hero_deadpond = session.exec(statement).one()
        if hero_deadpond.team:
            print("Deadpond pertenece al equipo:", hero_deadpond.team.name)


# ---------------------------------------------------------------------------
# 4) REMOVE RELATIONSHIPS
# ---------------------------------------------------------------------------
def update_heroes():
    with Session(engine) as session:
        statement = select(Hero).where(Hero.name == "Spider-Boy")
        hero_spider_boy = session.exec(statement).one()

        # Quitar la relación: se asigna None al atributo, igual que se
        # asignaría None a team_id. Esto NO borra a Spider-Boy, solo lo
        # desconecta del equipo (team_id queda NULL).
        hero_spider_boy.team = None
        session.add(hero_spider_boy)
        session.commit()
        session.refresh(hero_spider_boy)
        print("Spider-Boy sin equipo:", hero_spider_boy)


def main():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    create_db_and_tables()
    create_heroes()
    select_heroes()
    update_heroes()


if __name__ == "__main__":
    main()
