from sqlmodel import Session


with Session(engine) as session:

    hero = session.get(Hero, 1)

    if hero:

        # ----------------------------------------------------
        # ELIMINAMOS EL REGISTRO
        # ----------------------------------------------------
        #
        # A diferencia de hero.team = None,
        # aquí eliminamos el Hero de la BD.
        #
        session.delete(hero)

        session.commit()
