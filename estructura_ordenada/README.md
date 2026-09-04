# Snippets: Code Structure and Multiple Files (SQLModel)

Basado en: https://sqlmodel.tiangolo.com/tutorial/code-structure/

Dos formas de organizar un proyecto SQLModel con múltiples archivos, evitando
problemas de **imports circulares** entre `Hero` y `Team`.

## 1. `single_module_project/` — Opción simple (recomendada)

Todos los modelos viven en un único archivo `models.py`. Es la forma más
simple y la que conviene usar en la mayoría de los casos.

```
project/
├── __init__.py
├── app.py
├── database.py
└── models.py
```

Ejecutar:

```bash
python -m project.app
```

## 2. `separate_files_project/` — Opción avanzada

`Hero` y `Team` viven en archivos separados (`hero_model.py` y
`team_model.py`). Como cada uno referencia al otro, se usa el truco de
`TYPE_CHECKING` de `typing`:

- El import bajo `if TYPE_CHECKING:` solo existe para el editor (autocompletado,
  chequeo de tipos), no en tiempo de ejecución.
- Por eso la anotación se escribe como string: `Optional["Team"]` / `list["Hero"]`.

```
project/
├── __init__.py
├── app.py
├── database.py
├── hero_model.py
└── team_model.py
```

Ejecutar:

```bash
python -m project.app
```

## Notas clave

- El `__init__.py` vacío convierte la carpeta `project` en un paquete de
  Python, habilitando los imports relativos (`from .models import ...`).
- **Orden importa**: los modelos deben importarse *antes* de llamar a
  `SQLModel.metadata.create_all(engine)`, si no las tablas no se crean.
- Como ahora es un paquete y no un único archivo, se ejecuta con
  `python -m project.app` (con `-m`) en vez de `python app.py`.
