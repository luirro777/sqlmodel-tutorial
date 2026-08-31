from sqlmodel import Field, Relationship, SQLModel


class Team(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    name: str

    # --------------------------------------------------------
    # CASCADE DELETE
    # --------------------------------------------------------
    #
    # Si eliminamos un Team, SQLModel/SQLAlchemy
    # también eliminará sus Hero relacionados.
    #
    heroes: list["Hero"] = Relationship(
        back_populates="team",
        cascade_delete=True
    )


class Hero(SQLModel, table=True):

    id: int | None = Field(
        default=None,
        primary_key=True
    )

    name: str

    # --------------------------------------------------------
    # FOREIGN KEY
    # --------------------------------------------------------
    #
    # ondelete="CASCADE" establece también la regla
    # de eliminación en la Foreign Key.
    #
    team_id: int | None = Field(
        default=None,
        foreign_key="team.id",
        ondelete="CASCADE"
    )

    team: Team | None = Relationship(
        back_populates="heroes"
    )
