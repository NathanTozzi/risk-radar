import pytest
from sqlmodel import SQLModel, create_engine, Session
from fastapi.testclient import TestClient
from database import get_session
from main import app
from models import *

# Test database URL (in-memory SQLite for testing)
TEST_DATABASE_URL = "sqlite:///test.db"

@pytest.fixture(name="engine")
def engine_fixture():
    engine = create_engine(TEST_DATABASE_URL, echo=True)
    SQLModel.metadata.create_all(engine)
    yield engine

@pytest.fixture(name="session")
def session_fixture(engine):
    with Session(engine) as session:
        yield session

@pytest.fixture(name="client")
def client_fixture(session: Session):
    def get_session_override():
        yield session

    app.dependency_overrides[get_session] = get_session_override
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()