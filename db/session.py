from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from config import settings

# SQLite needs check_same_thread=False for multi-threaded use
engine_kwargs = {}
if settings.database_url.startswith("sqlite"):
    engine_kwargs["connect_args"] = {"check_same_thread": False}

engine = create_engine(
    settings.database_url,
    future=True,
    echo=settings.database_echo,
    **engine_kwargs
)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    # Import models to ensure they are registered on Base before create_all
    from .models import Base

    Base.metadata.create_all(bind=engine)
