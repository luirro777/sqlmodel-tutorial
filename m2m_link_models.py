from sqlmodel import (
    Field,
    Relationship,
    Session,
    SQLModel,
    create_engine,
    select,
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

    # Campo adicional de la relación.
    is_training: bool = False

    team: "Team" = Relationship(
        back_populates="hero_links"
    )

    hero: "Hero" = Relationship(
        back_populates="team_links"
    )


class Team(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    name: str = Field(index=True)

    headquarters: str

    hero_links: list[HeroTeamLink] = Relationship(
        back_populates="team"
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

    team_links: list[HeroTeamLink] = Relationship(
        back_populates="hero"
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
            secret_name="Dive Wilson"
        )

        rusty_man = Hero(
            name="Rusty-Man",
            secret_name="Tommy Sharp",
            age=48
        )

        spider_boy = Hero(
            name="Spider-Boy",
            secret_name="Pedro Parqueador"
        )

        # --------------------------------------------------------
        # Creamos las relaciones explícitamente.
        # --------------------------------------------------------

        deadpond_z_force = HeroTeamLink(
            team=z_force,
            hero=deadpond
        )

        deadpond_preventers = HeroTeamLink(
            team=preventers,
            hero=deadpond,
            is_training=True
        )

        spider_boy_preventers = HeroTeamLink(
            team=preventers,
            hero=spider_boy,
            is_training=True
        )

        rusty_man_preventers = HeroTeamLink(
            team=preventers,
            hero=rusty_man
        )

        # --------------------------------------------------------
        # Guardamos los Links.
        # --------------------------------------------------------

        session.add(deadpond_z_force)
        session.add(deadpond_preventers)
        session.add(spider_boy_preventers)
        session.add(rusty_man_preventers)

        session.commit()

        # --------------------------------------------------------
        # Leemos información de la relación.
        # --------------------------------------------------------

        for link in preventers.hero_links:

            print(
                "Hero:",
                link.hero.name
            )

            print(
                "Training:",
                link.is_training
            )


def update_data():

    with Session(engine) as session:

        spider_boy = session.exec(
            select(Hero)
            .where(
                Hero.name == "Spider-Boy"
            )
        ).one()

        z_force = session.exec(
            select(Team)
            .where(
                Team.name == "Z-Force"
            )
        ).one()

        # --------------------------------------------------------
        # Creamos una nueva relación.
        # --------------------------------------------------------

        spider_boy_z_force = HeroTeamLink(
            team=z_force,
            hero=spider_boy,
            is_training=True
        )

        z_force.hero_links.append(
            spider_boy_z_force
        )

        session.add(z_force)

        session.commit()

        # --------------------------------------------------------
        # Modificamos un campo de una relación existente.
        # --------------------------------------------------------

        for link in spider_boy.team_links:

            if link.team.name == "Preventers":

                link.is_training = False

        session.add(spider_boy)

        session.commit()

        # --------------------------------------------------------
        # Mostramos el resultado.
        # --------------------------------------------------------

        for link in spider_boy.team_links:

            print(
                "Team:",
                link.team.name
            )

            print(
                "Training:",
                link.is_training
            )


if __name__ == "__main__":

    create_db_and_tables()

    create_data()

    update_data()
