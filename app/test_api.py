from fastapi.testclient import TestClient
from sqlalchemy import create_engine, StaticPool
from sqlalchemy.orm import sessionmaker

from app.main import app, get_db
from app.database import Base
from app.models import Address

client = TestClient(app)
ADDRESS1 = {"id": 300, "name": "my new address", "latitude": 2.1, "longitude": 3.0}
ADDRESS2 = {"id": 400, "name": "my newer address", "latitude": 2.5, "longitude": 3.0}

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
        database.add(Address(**ADDRESS1))
        database.add(Address(**ADDRESS2))
        database.commit()
        database.close()

        yield database
    finally:
        # delete db before closing
        Base.metadata.drop_all(bind=engine)
        database.close()


app.dependency_overrides[get_db] = override_get_db


class TestGetAddressInRadius:
    URL = "/addresses/"

    def test_no_params(self):
        response = client.get(f"{self.URL}")
        data = response.json()

        assert response.status_code == 200
        assert len(data) == 2

    def test_missing_params(self):
        response = client.get(f"{self.URL}?lat=0&long=0")
        data = response.json()

        assert response.status_code == 422
        assert data["detail"] == "lat, long, or distance is missing from query params"

    def test_invalid_distance(self):
        response = client.get(f"{self.URL}?lat=33&long=22&distance=-0.1")
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "invalid distance. please enter non-negative values."

    def test_invalid_latitude(self):
        response = client.get(f"{self.URL}?lat=330&long=22&distance=0")
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "invalid latitude. please enter from -90.0 to 90.0"

    def test_invalid_longitude(self):
        response = client.get(f"{self.URL}?lat=33&long=220&distance=0")
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "invalid longitude. please enter from -180.0 to 180.0"

    def test_get_no_addresses_in_radius(self):
        response = client.get(f"{self.URL}?lat=33&long=22&distance=50")
        data = response.json()

        assert response.status_code == 200
        assert type(data) == list
        assert len(data) == 0

    def test_same_coordinates_and_zero_distance(self):
        response = client.get(
            f"{self.URL}?lat={ADDRESS1['latitude']}&long={ADDRESS1['longitude']}&distance=0"
        )
        data = response.json()

        assert response.status_code == 200
        assert type(data) == list
        assert len(data) == 1
        assert data[0]["name"] == ADDRESS1["name"]
        assert data[0]["latitude"] == ADDRESS1["latitude"]
        assert data[0]["longitude"] == ADDRESS1["longitude"]

    def test_get_addresses_in_radius(self):
        response = client.get(f"{self.URL}?lat=2.5&long=3&distance=50")
        data = response.json()

        assert response.status_code == 200
        assert type(data) == list
        assert data[0]["name"] == ADDRESS1["name"]
        assert data[0]["latitude"] == ADDRESS1["latitude"]
        assert data[0]["longitude"] == ADDRESS1["longitude"]
        assert data[1]["name"] == ADDRESS2["name"]
        assert data[1]["latitude"] == ADDRESS2["latitude"]
        assert data[1]["longitude"] == ADDRESS2["longitude"]


class TestCreateAddress:
    URL = "/addresses/"

    def test_create_duplicate_address(self):
        payload = ADDRESS1
        response = client.post(self.URL, json=payload)
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "duplicate coordinates"

    def test_invalid_latitude(self):
        payload = {"name": "test", "latitude": 91.0, "longitude": 2.3}
        response = client.post(self.URL, json=payload)
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "invalid latitude. please enter from -90.0 to 90.0"

    def test_invalid_longitude(self):
        payload = {"name": "test", "latitude": 1.2, "longitude": -180.1}
        response = client.post(self.URL, json=payload)
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "invalid longitude. please enter from -180.0 to 180.0"

    def test_create_address(self):
        payload = {"name": "test", "latitude": 1.2, "longitude": 2.3}
        response = client.post(self.URL, json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data["name"] == payload["name"]
        assert data["latitude"] == payload["latitude"]
        assert data["longitude"] == payload["longitude"]
        assert "id" in data


class TestUpdateAddress:
    URL = "/addresses/"

    def test_invalid_id(self):
        id = 200
        payload = {"name": "test", "latitude": 2.1, "longitude": 3.0}
        response = client.put(f"{self.URL}{id}", json=payload)
        data = response.json()

        assert response.status_code == 404
        assert data["detail"] == "id not found"

    def test_update_duplicate_coordinates(self):
        id = 400
        payload = {"name": "test", "latitude": 2.1, "longitude": 3.0}
        response = client.put(f"{self.URL}{id}", json=payload)
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "duplicate coordinates"

    def test_update_invalid_latitude(self):
        id = 400
        payload = {"name": "test", "latitude": 310, "longitude": 3.0}
        response = client.put(f"{self.URL}{id}", json=payload)
        data = response.json()

        assert response.status_code == 400
        assert data["detail"] == "invalid latitude. please enter from -90.0 to 90.0"

    def test_update_invalid_longitude(self):
        id = 400
        payload = {"name": "test", "latitude": 3, "longitude": -300}
        response = client.put(f"{self.URL}{id}", json=payload)
        data = response.json()

        print(data)
        assert response.status_code == 400
        assert data["detail"] == "invalid longitude. please enter from -180.0 to 180.0"

    def test_update_address(self):
        id = 300
        payload = {"name": "test", "latitude": 1.2, "longitude": 2.3}
        response = client.put(f"{self.URL}{id}", json=payload)
        data = response.json()

        assert response.status_code == 200
        assert data["name"] == payload["name"]
        assert data["latitude"] == payload["latitude"]
        assert data["longitude"] == payload["longitude"]
        assert data["id"] == id


class TestDeleteAddress:
    URL = "/addresses/"

    def test_delete_non_existent_id(self):
        response = client.delete(f"{self.URL}200")

        assert response.status_code == 204

    def test_delete_address(self):
        response = client.delete(f"{self.URL}400")

        assert response.status_code == 204
