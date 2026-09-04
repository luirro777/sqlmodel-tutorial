"""
03 - ondelete="SET NULL": borrar un Team NO borra sus Heroes,
                          solo les deja el team_id en NULL
================================================================

Diferencia clave con el script 02:
  - Acá el Relationship() de Team.heroes NO tiene cascade_delete.
  - El Field() de Hero.team_id tiene ondelete="SET NULL" en vez de CASCADE.

Importante (aunque no pongas ondelete="SET NULL"): por default,
SQLModel/SQLAlchemy YA pone en NULL el team_id de los heroes afectados
antes de borrar el team, desde el código Python. ondelete="SET NULL" es
un refuerzo a nivel de BASE DE DATOS, para el caso en que alguien borre
el team con SQL directo, sin pasar por esta app.

Ejecutar:  python 03_set_null.py
"""

import os
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    heroes: list["Hero"] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    # team_id TIENE que admitir None; si no, violarías el NOT NULL al
    # ponerlo en NULL.
    team_id: int | None = Field(
        default=None, foreign_key="team.id", ondelete="SET NULL"
    )
    team: Team | None = Relationship(back_populates="heroes")


sqlite_file_name = "set_null.db"
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


def select_orphan_heroes():
    with Session(engine) as session:
        for name in ("Black Lion", "Princess Sure-E"):
            statement = select(Hero).where(Hero.name == name)
            hero = session.exec(statement).first()
            print(f"{name} sigue existiendo, sin equipo:", hero)


def main():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    create_db_and_tables()
    create_heroes()
    delete_team()
    select_orphan_heroes()  # esperado: los heroes siguen ahí, team_id=None


if __name__ == "__main__":
    main()
