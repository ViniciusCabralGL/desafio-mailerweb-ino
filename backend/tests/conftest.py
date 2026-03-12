import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import Base, get_db
from app.core.security import get_password_hash
from app.models.user import User
from app.models.room import Room

# Use SQLite for testing
SQLALCHEMY_DATABASE_URL = "sqlite:///:memory:"

engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def override_get_db():
    db = TestingSessionLocal()
    try:
        yield db
    finally:
        db.close()


app.dependency_overrides[get_db] = override_get_db


@pytest.fixture(scope="function")
def db():
    Base.metadata.create_all(bind=engine)
    db = TestingSessionLocal()
    yield db
    db.close()
    Base.metadata.drop_all(bind=engine)


@pytest.fixture(scope="function")
def client(db):
    Base.metadata.create_all(bind=engine)
    yield TestClient(app)
    Base.metadata.drop_all(bind=engine)


@pytest.fixture
def test_user(db):
    user = User(
        email="test@example.com",
        name="Test User",
        hashed_password=get_password_hash("testpassword123")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@pytest.fixture
def test_room(db):
    room = Room(
        name="Sala de Reuniões 1",
        capacity=10,
        description="Sala principal"
    )
    db.add(room)
    db.commit()
    db.refresh(room)
    return room


@pytest.fixture
def auth_headers(client, test_user):
    response = client.post(
        "/api/auth/login",
        data={
            "username": "test@example.com",
            "password": "testpassword123"
        }
    )
    token = response.json()["access_token"]
    return {"Authorization": f"Bearer {token}"}
