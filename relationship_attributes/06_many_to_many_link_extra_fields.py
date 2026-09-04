"""
06 - MANY-TO-MANY con datos extra en el link: HeroTeamLink.is_training
=========================================================================

Cubre: Link Model with Extra Fields

Diferencia de fondo con 05_many_to_many_simple.py: acá SÍ interactuamos
directamente con HeroTeamLink como un modelo más, porque necesitamos
guardar un dato que no pertenece ni al hero ni al team, sino
específicamente A LA RELACIÓN entre ambos (is_training).

Para lograrlo, HeroTeamLink deja de ser solo una tabla de enlace pasiva
y se convierte en el centro de DOS relaciones one-to-many explícitas:
  - Team  <-- hero_links -->  HeroTeamLink  <-- team -- (uno)
  - Hero  <-- team_links -->  HeroTeamLink  <-- hero -- (uno)

Por eso Team.heroes / Hero.teams desaparecen, y en su lugar aparecen
Team.hero_links / Hero.team_links: ya no apuntan directo al otro modelo,
apuntan a la fila de la relación (que a su vez apunta al otro modelo).

Ejecutar:  python 07_many_to_many_link_extra_fields.py
"""

import os
from sqlmodel import Field, Relationship, Session, SQLModel, create_engine, select


class HeroTeamLink(SQLModel, table=True):
    team_id: int | None = Field(default=None, foreign_key="team.id", primary_key=True)
    hero_id: int | None = Field(default=None, foreign_key="hero.id", primary_key=True)
    is_training: bool = False

    # Estas SÍ son relaciones "normales" de uno a muchos, no many-to-many:
    # cada fila de HeroTeamLink apunta a UN Team y a UN Hero.
    team: "Team" = Relationship(back_populates="hero_links")
    hero: "Hero" = Relationship(back_populates="team_links")


class Team(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    headquarters: str

    hero_links: list[HeroTeamLink] = Relationship(back_populates="team")


class Hero(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True)
    secret_name: str
    age: int | None = Field(default=None, index=True)

    team_links: list[HeroTeamLink] = Relationship(back_populates="hero")


sqlite_file_name = "many_to_many_extra_fields.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)


def create_db_and_tables():
    SQLModel.metadata.create_all(engine)


def create_heroes():
    with Session(engine) as session:
        team_preventers = Team(name="Preventers", headquarters="Sharp Tower")
        team_z_force = Team(name="Z-Force", headquarters="Sister Margaret's Bar")

        hero_deadpond = Hero(name="Deadpond", secret_name="Dive Wilson")
        hero_rusty_man = Hero(name="Rusty-Man", secret_name="Tommy Sharp", age=48)
        hero_spider_boy = Hero(name="Spider-Boy", secret_name="Pedro Parqueador")

        # Acá SÍ creamos HeroTeamLink a mano, porque es donde vive
        # is_training. Cada instancia es una fila de la tabla de enlace.
        deadpond_team_z_link = HeroTeamLink(team=team_z_force, hero=hero_deadpond)
        deadpond_preventers_link = HeroTeamLink(
            team=team_preventers, hero=hero_deadpond, is_training=True
        )
        spider_boy_preventers_link = HeroTeamLink(
            team=team_preventers, hero=hero_spider_boy, is_training=True
        )
        rusty_man_preventers_link = HeroTeamLink(
            team=team_preventers, hero=hero_rusty_man
        )

        # Solo agregamos los links a la sesión: como cada link está
        # conectado a un hero y a un team, esos también se agregan solos.
        session.add(deadpond_team_z_link)
        session.add(deadpond_preventers_link)
        session.add(spider_boy_preventers_link)
        session.add(rusty_man_preventers_link)
        session.commit()

        for link in team_z_force.hero_links:
            print("Z-Force, hero:", link.hero.name, "- entrenando:", link.is_training)

        for link in team_preventers.hero_links:
            print("Preventers, hero:", link.hero.name, "- entrenando:", link.is_training)


def update_heroes():
    with Session(engine) as session:
        hero_spider_boy = session.exec(
            select(Hero).where(Hero.name == "Spider-Boy")
        ).one()
        team_z_force = session.exec(select(Team).where(Team.name == "Z-Force")).one()

        # --- Agregar la relación: crear un link nuevo y hacer append ---
        # (No hay un equivalente directo a "team.heroes.append(hero)"
        # porque ahora la lista es de links, no de heroes.)
        spider_boy_z_force_link = HeroTeamLink(
            team=team_z_force, hero=hero_spider_boy, is_training=True
        )
        # Acá agregamos el link EXPLÍCITAMENTE, y ANTES de appendearlo a la
        # lista (a diferencia del script 05, donde alcanzaba con
        # session.add(team)). Es porque HeroTeamLink es ahora un modelo con
        # su propio ciclo de vida, no una tabla que SQLAlchemy gestiona de
        # forma transparente por detrás. Si lo agregás DESPUÉS del append,
        # SQLAlchemy intenta un autoflush en el medio y tira un warning.
        session.add(spider_boy_z_force_link)
        team_z_force.hero_links.append(spider_boy_z_force_link)
        session.add(team_z_force)
        session.commit()

        print("Links de Spider-Boy tras el append:", hero_spider_boy.team_links)
        print("Links de Z-Force tras el append:", team_z_force.hero_links)

        # --- Actualizar un dato DE LA RELACIÓN, no del hero ni del team ---
        # Spider-Boy termina su entrenamiento en Preventers.
        for link in hero_spider_boy.team_links:
            if link.team.name == "Preventers":
                link.is_training = False

        session.add(hero_spider_boy)
        session.commit()

        for link in hero_spider_boy.team_links:
            print(
                "Spider-Boy - equipo:", link.team.name,
                "- entrenando:", link.is_training,
            )


def main():
    if os.path.exists(sqlite_file_name):
        os.remove(sqlite_file_name)
    create_db_and_tables()
    create_heroes()
    update_heroes()


if __name__ == "__main__":
    main()
