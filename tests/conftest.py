import sys
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.append(str(PROJECT_ROOT))

from api.dependencies import get_db
from api import main as api_main
from config import settings
from db.models import Base


@pytest.fixture(scope="session", autouse=True)
def configure_test_settings():
    original = {
        "jwt_secret": settings.jwt_secret,
        "jwt_algorithm": settings.jwt_algorithm,
        "use_s3": settings.use_s3,
        "s3_bucket": settings.s3_bucket,
        "redis_url": settings.redis_url,
    }
    settings.jwt_secret = "test-secret"
    settings.jwt_algorithm = "HS256"
    settings.use_s3 = False
    settings.s3_bucket = "test-bucket"
    settings.redis_url = "redis://localhost:6379/0"
    yield
    for key, value in original.items():
        setattr(settings, key, value)


@pytest.fixture(scope="session")
def db_engine(tmp_path_factory):
    db_path = tmp_path_factory.mktemp("db") / "test.db"
    engine = create_engine(f"sqlite:///{db_path}", connect_args={"check_same_thread": False})
    Base.metadata.create_all(bind=engine)
    yield engine
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def db_session(db_engine):
    TestingSessionLocal = sessionmaker(bind=db_engine, autoflush=False, autocommit=False)
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.rollback()
        for table in reversed(Base.metadata.sorted_tables):
            session.execute(table.delete())
        session.commit()
        session.close()


@pytest.fixture
def app_client(db_session):
    app = api_main.app

    def override_get_db():
        yield db_session

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()


@pytest.fixture
def mock_redis(monkeypatch):
    import fakeredis

    fake = fakeredis.FakeRedis()
    monkeypatch.setattr("background.queue.get_redis_conn", lambda: fake)
    return fake


@pytest.fixture
def mock_queue(monkeypatch, mock_redis):
    from rq import Queue

    queue = Queue("default", connection=mock_redis)
    monkeypatch.setattr("background.queue.get_queue", lambda name="default": queue)
    return queue
