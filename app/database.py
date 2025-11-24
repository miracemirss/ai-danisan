# app/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

from app.core.config import settings


DATABASE_URL = (
    f"postgresql+psycopg2://{settings.DB_USER}:"
    f"{settings.DB_PASSWORD}@{settings.DB_HOST}:"
    f"{settings.DB_PORT}/{settings.DB_NAME}"
)


engine = create_engine(
    DATABASE_URL,
    echo=False,          # SQL logları görmek istersen True yap
    future=True
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()


# --- Dependency Injection ---
def get_db():
    """
    FastAPI dependency:
    - session açar
    - endpoint bitince otomatik kapatır
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
