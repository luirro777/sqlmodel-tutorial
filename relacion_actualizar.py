from sqlmodel import Session


with Session(engine) as session:

    # Buscamos el Hero
    hero = session.get(Hero, 1)

    # Buscamos otro Team
    new_team = session.get(Team, 2)

    if hero and new_team:

        # ----------------------------------------------------
        # Cambiamos la relación
        # ----------------------------------------------------
        #
        # El Hero deja de pertenecer a su Team anterior
        # y pasa a pertenecer al nuevo Team.
        #
        hero.team = new_team

        session.add(hero)

        session.commit()
