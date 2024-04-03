from haversine import haversine
from sqlalchemy.orm import Session

from . import models, schemas


def get_address_by_coordinates(db: Session, latitude: float, longitude: float):
    address = (
        db.query(models.Address)
        .filter_by(latitude=latitude, longitude=longitude)
        .first()
    )

    return address


def __get_addresses_in_radius(
    db: Session, latitude: float, longitude: float, distance: float
):
    """
    initial implementation for get addresses in radius
    however, i always get this error
        TypeError: Boolean value of this clause is not defined
    i am not entirely sure why this happens but i think using `models.Address.<lat | long>`
      inside a function, the value itself is not passed but an `InstrumentedAttribute` instead
    """
    addresses = (
        db.query(models.Address)
        .filter(
            haversine(
                (models.Address.latitude, models.Address.longitude),
                (latitude, longitude),
            )
            <= distance
        )
        .all()
    )

    return addresses


def is_in_radius(
    coordinates: tuple[float, float],
    starting_coordinates: tuple[float, float],
    radius: float,
):
    """
    check if the distance of the two given coordinates is within
    the given radius
    """
    if haversine(coordinates, starting_coordinates) <= radius:
        return True

    return False


def get_addresses_in_radius(
    db: Session, coordinates: tuple[float, float], distance: float
):
    addresses = db.query(models.Address).all()

    # TODO: filter out in query for optimization
    # manually filtered out since initial implementation has errors
    filtered_addresses = list(
        filter(
            lambda address: is_in_radius(
                (address.latitude, address.longitude), coordinates, distance
            ),
            addresses,
        )
    )

    return filtered_addresses


def create_address(db: Session, address: schemas.AddressCreate):
    new_address = models.Address(**address.model_dump())

    if new_address.latitude < -90.0 or new_address.latitude > 90.0:
        raise ValueError("invalid latitude. please enter from -90.0 to 90.0")

    if new_address.longitude < -180.0 or new_address.longitude > 180.0:
        raise ValueError("invalid longitude. please enter from -180.0 to 180.0")

    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address
