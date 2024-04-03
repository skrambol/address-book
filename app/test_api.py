from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base
from app.models import Address

client = TestClient(app)
NEW_ADDRESS = {"name": "my new address", "latitude": 2.1, "longitude": 3.0}

# setup db
engine = create_engine(
    "sqlite:///:memory:",  # in-memory db for testing,
    connect_args={
        "check_same_thread": False,
    },
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
database = TestingSessionLocal()


# use test db instead of file db
def override_get_db():
    try:
        # setup db content
        Base.metadata.create_all(bind=engine)
        new_address = Address(**NEW_ADDRESS)
        database.add(new_address)
        database.commit()
        database.close()

        yield database
    finally:
        # delete db before closing
        Base.metadata.drop_all(bind=engine)
        database.close()


app.dependency_overrides[get_db] = override_get_db


class TestGetAddressInRadius:
    def test_get_no_addresses_in_radius(self):
        response = client.get(f"/addresses/?lat=33&long=22&distance=50")
        data = response.json()

        assert response.status_code == 200
        assert type(data) == list
        assert len(data) == 0

    def test_same_coordinates_and_zero_distance(self):
        response = client.get(
            f"/addresses/?lat={NEW_ADDRESS['latitude']}&long={NEW_ADDRESS['longitude']}&distance=0"
        )
        data = response.json()

        assert response.status_code == 200
        assert type(data) == list
        assert len(data) == 1
        assert data[0]["name"] == NEW_ADDRESS["name"]
        assert data[0]["latitude"] == NEW_ADDRESS["latitude"]
        assert data[0]["longitude"] == NEW_ADDRESS["longitude"]

    def test_get_addresses_in_radius(self):
        response = client.get(f"/addresses/?lat=2.5&long=3&distance=50")
        data = response.json()

        assert response.status_code == 200
        assert type(data) == list
        assert data[0]["name"] == NEW_ADDRESS["name"]
        assert data[0]["latitude"] == NEW_ADDRESS["latitude"]
        assert data[0]["longitude"] == NEW_ADDRESS["longitude"]



class TestCreateAddress:
    def test_create_duplicate_address(self):
        payload = NEW_ADDRESS
        response = client.post("/addresses/", json=payload)
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "duplicate coordinates"

    def test_invalid_latitude(self):
        payload = {"name": "test", "latitude": 91.0, "longitude": 2.3}
        response = client.post("/addresses/", json=payload)
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "invalid latitude. please enter from -90.0 to 90.0"

    def test_invalid_longitude(self):
        payload = {"name": "test", "latitude": 1.2, "longitude": -180.1}
        response = client.post("/addresses/", json=payload)
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "invalid longitude. please enter from -180.0 to 180.0"

    def test_create_address(self):
        payload = {"name": "test", "latitude": 1.2, "longitude": 2.3}
        response = client.post("/addresses/", json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data["name"] == payload["name"]
        assert data["latitude"] == payload["latitude"]
        assert data["longitude"] == payload["longitude"]
        assert "id" in data
