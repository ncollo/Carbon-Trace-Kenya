from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:pass@localhost:5432/carbon"

engine = create_engine(DATABASE_URL, future=True)
SessionLocal = sessionmaker(bind=engine, autoflush=False, autocommit=False)


def init_db():
    # Import models to ensure they are registered on Base before create_all
    from .models import Base

    Base.metadata.create_all(bind=engine)
