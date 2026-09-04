"""
02 - CASCADE DELETE: borrar un Team borra automáticamente sus Heroes
=====================================================================

cascade_delete=True     -> se configura en el Relationship(), en el lado
                            SIN foreign key (Team).
ondelete="CASCADE"      -> se configura en el Field(), en el lado
                            CON foreign key (Hero.team_id).

Usar los dos juntos cubre la mayoría de los casos:
  - cascade_delete=True: SQLAlchemy borra los heroes en Python al hacer
    session.delete(team) + commit.
  - ondelete="CASCADE": el motor de la base de datos también sabe borrar
    los heroes si alguien borra el team directamente con SQL (sin pasar
    por nuestro código).

Ejecutar:  python 02_cascade_delete.py
"""

import os
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: list["Hero"] = Relationship(back_populates="team", cascade_delete=True)


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    team_id: int | None = Field(
        default=None, foreign_key="team.id", ondelete="CASCADE"
    )
    team: Team | None = Relationship(back_populates="heroes")


sqlite_file_name = "cascade_delete.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    with Session(engine) as session:
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
        print("Team creado:", team_wakaland)


def delete_team():
    with Session(engine) as session:
        statement = select(Team).where(Team.name == "Wakaland")
        team = session.exec(statement).one()
        session.delete(team)
        session.commit()
        print("Team borrado:", team)


def select_deleted_heroes():
    with Session(engine) as session:
        for name in ("Black Lion", "Princess Sure-E"):
            statement = select(Hero).where(Hero.name == name)
            hero = session.exec(statement).first()
            print(f"{name} ya no existe en la base:", hero)


def main():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    create_db_and_tables()
    create_heroes()
    delete_team()
    select_deleted_heroes()  # esperado: None, None -> se borraron en cascada


if __name__ == "__main__":
    main()
