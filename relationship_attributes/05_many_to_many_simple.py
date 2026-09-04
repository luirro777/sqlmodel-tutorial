"""
05 - MANY-TO-MANY (simple): un Hero puede estar en varios Teams,
                             un Team puede tener varios Heroes
=================================================================

Cubre:
  - Create Models with a Many-to-Many Link
  - Create Data with Many-to-Many Relationships
  - Update and Remove Many-to-Many Relationships

La pieza nueva es HeroTeamLink: una tabla de enlace (link table) con dos
columnas, cada una FK a una tabla distinta, y las DOS son primary_key en
conjunto (primary key compuesta). Eso es lo que hace que cada par
(team_id, hero_id) sea único: un hero no puede estar dos veces en el
mismo team.

Con link_model=HeroTeamLink pasado en el Relationship(), NUNCA
interactuamos directamente con HeroTeamLink: SQLModel/SQLAlchemy inserta,
borra y consulta esa tabla intermedia por nosotros solamente con
list.append() / list.remove() sobre `hero.teams` o `team.heroes`.

Ejecutar:  python 06_many_to_many_simple.py
"""

import os
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class HeroTeamLink(SQLModel, table=True):
    # Primary key COMPUESTA: la combinación (team_id, hero_id) es lo que
    # se garantiza único, no cada columna por separado.
    team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: list["Hero"] = Relationship(back_populates="teams", link_model=HeroTeamLink)


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    # Ya NO hay team_id acá: la relación many-to-many vive en la tabla
    # de enlace, no en una columna de hero.
    teams: list[Team] = Relationship(back_populates="heroes", link_model=HeroTeamLink)


sqlite_file_name = "many_to_many_simple.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    with Session(engine) as session:
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")

        # teams= recibe una LISTA, porque un hero puede pertenecer a
        # varios equipos a la vez.
        hero_deadpond = Hero(
            name="Deadpond",
            secret_name="Dive Wilson",
            teams=[team_z_force, team_preventers],
        )
        hero_rusty_man = Hero(
            name="Rusty-Man",
            secret_name="Tommy Sharp",
            age=48,
            teams=[team_preventers],
        )
        hero_spider_boy = Hero(
            name="Spider-Boy", secret_name="Pedro Parqueador", teams=[team_preventers]
        )
        session.add(hero_deadpond)
        session.add(hero_rusty_man)
        session.add(hero_spider_boy)
        session.commit()

        session.refresh(hero_deadpond)
        session.refresh(hero_rusty_man)
        session.refresh(hero_spider_boy)

        print("Deadpond:", hero_deadpond)
        print("Deadpond teams:", hero_deadpond.teams)
        print("Rusty-Man:", hero_rusty_man)
        print("Rusty-Man teams:", hero_rusty_man.teams)
        print("Spider-Boy:", hero_spider_boy)
        print("Spider-Boy teams:", hero_spider_boy.teams)


def update_heroes():
    with Session(engine) as session:
        hero_spider_boy = session.exec(
            select(Hero).where(Hero.name == "Spider-Boy")
        ).one()
        team_z_force = session.exec(select(Team).where(Team.name == "Z-Force")).one()

        # --- Agregar una relación many-to-many: append() ---
        # Spider-Boy se suma a Z-Force sin dejar Preventers.
        team_z_force.heroes.append(hero_spider_boy)
        session.add(team_z_force)
        session.commit()

        # Ojo: no hicimos session.refresh(hero_spider_boy) ni lo agregamos
        # a la sesión, y aun así hero_spider_boy.teams está actualizado.
        # Eso es back_populates + acceso al atributo disparando un refresh
        # automático.
        print("Teams de Spider-Boy tras el append:", hero_spider_boy.teams)
        print("Heroes de Z-Force tras el append:", team_z_force.heroes)

        # --- Quitar una relación many-to-many: remove() ---
        hero_spider_boy.teams.remove(team_z_force)
        session.add(team_z_force)
        session.commit()

        print("Heroes de Z-Force tras el remove:", team_z_force.heroes)
        print("Teams de Spider-Boy tras el remove:", hero_spider_boy.teams)


def main():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    create_db_and_tables()
    create_heroes()
    update_heroes()


if __name__ == "__main__":
    main()
