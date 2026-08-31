from sqlmodel import (
    Field,
    Relationship,
    Session,
    SQLModel,
    create_engine,
    select,
)


# ============================================================
# MODELOS
# ============================================================

class Team(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    name: str

    # Un Team tiene muchos Hero
    heroes: list["Hero"] = Relationship(
        back_populates="team"
    )


class Hero(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    name: str

    # Foreign Key hacia team.id
    team_id: int | None = Field(
        default=None,
        foreign_key="team.id"
    )

    # Relationship hacia Team
    team: Team | None = Relationship(
        back_populates="heroes"
    )


# ============================================================
# DATABASE
# ============================================================

engine = create_engine(
    "sqlite:///heroes.db",
    echo=True
)

SQLModel.metadata.create_all(engine)


# ============================================================
# CREATE
# ============================================================

with Session(engine) as session:

    # Creamos un Team
    team = Team(
        name="Avengers"
    )

    # Creamos un Hero y establecemos la relación
    # directamente utilizando el objeto Team.
    hero = Hero(
        name="Iron Man",
        team=team
    )

    # Agregamos el Hero.
    #
    # SQLModel/SQLAlchemy se encargará de persistir
    # también el Team relacionado.
    session.add(hero)

    session.commit()


# ============================================================
# READ
# ============================================================

with Session(engine) as session:

    # Buscamos un Hero
    hero = session.exec(
        select(Hero)
        .where(Hero.name == "Iron Man")
    ).one()

    print("Hero:", hero.name)

    # --------------------------------------------------------
    # Accedemos al objeto Team mediante Relationship
    # --------------------------------------------------------

    if hero.team:

        print(
            "Team:",
            hero.team.name
        )

    # --------------------------------------------------------
    # Accedemos directamente a la Foreign Key
    # --------------------------------------------------------

    print(
        "Team ID:",
        hero.team_id
    )
