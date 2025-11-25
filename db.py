from sqlmodel import SQLModel, create_engine

from config import DATABASE_URL

# Motor de base de datos
engine = create_engine(DATABASE_URL, echo=False)


def init_db() -> None:
    """Crea tablas si no existen."""
    SQLModel.metadata.create_all(engine)
