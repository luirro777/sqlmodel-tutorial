from sqlmodel import (
    Field,
    Relationship,
    Session,
    SQLModel,
    create_engine,
)


class HeroTeamLink(SQLModel, table=True):

    team_id: int | None = Field(
        default=None,
        foreign_key="team.id",
        primary_key=True
    )

    hero_id: int | None = Field(
        default=None,
        foreign_key="hero.id",
        primary_key=True
    )


class Team(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(index=True)

    headquarters: str

    heroes: list["Hero"] = Relationship(
        back_populates="teams",
        link_model=HeroTeamLink
    )


class Hero(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(index=True)

    secret_name: str

    age: int | None = Field(
        default=None,
        index=True
    )

    teams: list[Team] = Relationship(
        back_populates="heroes",
        link_model=HeroTeamLink
    )


engine = create_engine(
    "sqlite:///database.db",
    echo=True
)


def create_db_and_tables():

    SQLModel.metadata.create_all(
        engine
    )


def create_data():

    with Session(engine) as session:

        preventers = Team(
            name="Preventers",
            headquarters="Sharp Tower"
        )

        z_force = Team(
            name="Z-Force",
            headquarters="Sister Margaret's Bar"
        )

        deadpond = Hero(
            name="Deadpond",
            secret_name="Dive Wilson",
            teams=[
                preventers,
                z_force
            ]
        )

        rusty_man = Hero(
            name="Rusty-Man",
            secret_name="Tommy Sharp",
            age=48,
            teams=[
                preventers
            ]
        )

        spider_boy = Hero(
            name="Spider-Boy",
            secret_name="Pedro Parqueador",
            teams=[
                preventers
            ]
        )

        session.add(deadpond)
        session.add(rusty_man)
        session.add(spider_boy)

        session.commit()

        print(
            "Deadpond teams:",
            deadpond.teams
        )

        print(
            "Preventers heroes:",
            preventers.heroes
        )


if __name__ == "__main__":

    create_db_and_tables()

    create_data()
