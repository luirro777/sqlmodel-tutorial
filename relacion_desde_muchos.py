from sqlmodel import Field, Relationship, Session, SQLModel, create_engine


class Team(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    name: str

    # Un Team puede tener muchos Hero
    heroes: list["Hero"] = Relationship(
        back_populates="team"
    )


class Hero(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    name: str

    team_id: int | None = Field(
        default=None,
        foreign_key="team.id"
    )

    team: Team | None = Relationship(
        back_populates="heroes"
    )


engine = create_engine(
    "sqlite:///heroes.db"
)

SQLModel.metadata.create_all(engine)


with Session(engine) as session:

    # --------------------------------------------------------
    # Creamos el Team
    # --------------------------------------------------------

    team = Team(
        name="Avengers"
    )

    # --------------------------------------------------------
    # Agregamos varios Hero a la colección
    # --------------------------------------------------------

    team.heroes.append(
        Hero(name="Iron Man")
    )

    team.heroes.append(
        Hero(name="Thor")
    )

    team.heroes.append(
        Hero(name="Captain America")
    )

    # --------------------------------------------------------
    # Guardamos el Team
    # --------------------------------------------------------

    session.add(team)

    session.commit()


# ============================================================
# LEER LA COLECCIÓN
# ============================================================

with Session(engine) as session:

    team = session.get(Team, 1)

    if team:

        print("Team:", team.name)

        # team.heroes es una lista de Hero
        for hero in team.heroes:

            print(
                "-",
                hero.name
            )
