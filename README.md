# SQLModel — Tutorial y Ejemplos

Repositorio de práctica siguiendo el [tutorial oficial de SQLModel](https://sqlmodel.tiangolo.com/tutorial/), con ejemplos de modelos, relaciones, CRUD y organización de código.

## Estructura del repositorio

```
.
├── app.py
├── estructura_ordenada/
└── relationship_attributes/
```

### `app.py`

Script principal de práctica que recorre gran parte del tutorial en un único archivo. Define tres modelos (`Team`, `Hero`, `Gadget`, este último relacionado con `Hero` por `hero_id`) y una serie de funciones que cubren el ciclo CRUD completo y varias formas de consulta:

- **Create**
  - `create_heroes()` — crea equipos y héroes, algunos asociados a un `team_id` y otros sin equipo.
  - `create_gadgets()` — crea gadgets asociados a héroes puntuales.
- **Read**
  - `find_specific_heroes()` — filtro combinado con `or_`, `col().in_()` y comparaciones.
  - `get_heroes_and_headquarters()` — `JOIN` entre `Hero` y `Team` para mostrar el cuartel de cada héroe.
  - `paginate_heroes(page, page_size)` — paginación con `offset` y `limit`.
  - `select_heroes()` — ejemplos comentados de distintas variantes de `SELECT` (`JOIN` con `where`, `JOIN` explícito, `LEFT OUTER JOIN`, filtros, `.first()`, `.one()`, `get()` por id, paginación manual).
- **Update**
  - `update_heroes()` — actualiza edad y equipo de un héroe.
  - `transfer_or_reassign_hero()` — reasigna un héroe a otro equipo.
  - `break_connection()` — rompe la relación héroe-equipo poniendo `team_id = None`.
- **Delete**
  - `delete_heroes()` — elimina un héroe y verifica que ya no exista.

La función `main()` arma la base de datos SQLite (`database.db`), crea las tablas y ejecuta la secuencia de creación y consulta. Las funciones de update/delete están comentadas en `main()` para poder habilitarlas de a una según lo que se quiera probar.

Para ejecutarlo (con el entorno virtual ya activado, ver [Instalación](#instalación)):

```bash
python app.py
```

### `estructura_ordenada/`

Corresponde a la sección [Code Structure and Multiple Files](https://sqlmodel.tiangolo.com/tutorial/code-structure/) del tutorial. Muestra dos formas de organizar un proyecto SQLModel en varios archivos en lugar de uno solo, evitando problemas de imports circulares entre `Hero` y `Team`:

- **`single_module_project/`** — todos los modelos en un único `models.py`, más `database.py` y `app.py`. Es el enfoque recomendado para la mayoría de los casos.
- **`separate_files_project/`** — `Hero` y `Team` en archivos separados (`hero_model.py`, `team_model.py`), usando `TYPE_CHECKING` para resolver la referencia circular solo a nivel de tipado, sin afectar el runtime.


Ver el `README.md` dentro de esta carpeta para más detalle.

### `relationship_attributes/`

Corresponde a la sección [Relationship Attributes](https://sqlmodel.tiangolo.com/tutorial/relationship-attributes/) del tutorial. Contiene los scripts que muestran cómo trabajar con los atributos de relación de SQLModel (a diferencia de usar solo `team_id` a mano como en `app.py`), incluyendo:

- Definición de relaciones con `Relationship()` y `back_populates`.
- Creación y actualización de datos a través de las relaciones (en vez de asignar el id foráneo directamente).
- Lectura de datos relacionados navegando los atributos (`hero.team`, `team.heroes`).
- Eliminación de relaciones.

## Requisitos

- Python 3.10+
- [SQLModel](https://sqlmodel.tiangolo.com/)

## Instalación

El proyecto se ejecuta dentro de un entorno virtual:

```bash
python -m venv venv
source venv/bin/activate   # En Windows: venv\Scripts\activate
pip install sqlmodel
```

Con el entorno activado, correr cualquiera de los scripts como se indica en cada sección de arriba.
