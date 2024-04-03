from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base

client = TestClient(app)

engine = create_engine(
    "sqlite:///:memory:",  # in-memory db for testing,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


Base.metadata.create_all(bind=engine)


# use test db instead of file db
def override_get_db():
    try:
        database = TestingSessionLocal()
        yield database
    finally:
        database.close()


app.dependency_overrides[get_db] = override_get_db


def test_create_address():
    payload = {"name": "test", "latitude": 1.2, "longitude": 2.3}
    response = client.post("/addresses/", json=payload)
    data = response.json()

    assert response.status_code == 200, response.text
    assert data["name"] == payload["name"]
    assert data["latitude"] == payload["latitude"]
    assert data["longitude"] == payload["longitude"]
    assert "id" in data
