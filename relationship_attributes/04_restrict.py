"""
04 - ondelete="RESTRICT": la base de datos IMPIDE borrar un Team
                          si todavía tiene Heroes
====================================================================

Piezas necesarias, las tres juntas:
  1) ondelete="RESTRICT" en Hero.team_id (Field).
  2) passive_deletes="all" en Team.heroes (Relationship): le dice a
     SQLAlchemy que NO intente poner los team_id en NULL antes de borrar
     -eso es justamente lo que queremos evitar, para que la restricción
     de la base de datos se dispare.
  3) PRAGMA foreign_keys=ON: SQLite ignora las foreign keys por default,
     hay que habilitarlas a mano para que RESTRICT funcione.

Este script demuestra el error, y después la forma correcta de resolverlo:
team.heroes.clear() para desasociar los heroes ANTES de borrar el team.

Ejecutar:  python 04_restrict.py
"""

import os
from sqlmodel import (
    Field,
    Relationship,
    Session,
    SQLModel,
    create_engine,
    select,
    text,
)
from sqlalchemy.exc import IntegrityError


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: list["Hero"] = Relationship(back_populates="team", passive_deletes="all")


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    team_id: int | None = Field(
        default=None, foreign_key="team.id", ondelete="RESTRICT"
    )
    team: Team | None = Relationship(back_populates="heroes")


sqlite_file_name = "restrict.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)
    with engine.connect() as connection:
        connection.execute(text("PRAGMA foreign_keys=ON"))  # necesario en SQLite


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


def try_delete_team_with_heroes():
    """Esto va a fallar: la base de datos rechaza el DELETE."""
    with Session(engine) as session:
        statement = select(Team).where(Team.name == "Wakaland")
        team = session.exec(statement).one()
        try:
            session.delete(team)
            session.commit()
            print("⚠️ Esto no debería imprimirse, se esperaba un error")
        except IntegrityError:
            session.rollback()
            print("✅ Error esperado: no se puede borrar un Team con Heroes")


def remove_team_heroes():
    """Solución: desasociar los heroes antes de borrar el team."""
    with Session(engine) as session:
        statement = select(Team).where(Team.name == "Wakaland")
        team = session.exec(statement).one()
        team.heroes.clear()  # pone team_id=None en cada hero
        session.add(team)
        session.commit()
        session.refresh(team)
        print("Team sin heroes:", team)


def delete_team():
    with Session(engine) as session:
        statement = select(Team).where(Team.name == "Wakaland")
        team = session.exec(statement).one()
        session.delete(team)
        session.commit()
        print("Team borrado, ahora sí:", team)


def main():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    create_db_and_tables()
    create_heroes()
    try_delete_team_with_heroes()
    remove_team_heroes()
    delete_team()


if __name__ == "__main__":
    main()
