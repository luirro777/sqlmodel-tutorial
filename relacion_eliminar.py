from sqlmodel import Session


with Session(engine) as session:

    hero = session.get(Hero, 1)

    if hero:

        # ----------------------------------------------------
        # ELIMINAMOS LA RELACIÓN
        # ----------------------------------------------------
        #
        # El Hero sigue existiendo.
        #
        # Lo que hacemos es indicar que ya no pertenece
        # a ningún Team.
        #
        hero.team = None

        session.add(hero)

        session.commit()
