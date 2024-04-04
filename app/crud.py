from haversine import haversine
from loguru import logger
from sqlalchemy.orm import Session

from . import models, schemas


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
    distance = haversine(coordinates, starting_coordinates)
    logger.debug(f"h({coordinates}, {starting_coordinates}) = {distance}; radius = {radius}")
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

    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address


def update_address(db: Session, id: int, address: schemas.AddressUpdate):
    db_address = db.get(models.Address, id)

    if db_address:
        db_address.name = address.name
        db_address.latitude = address.latitude
        db_address.longitude = address.longitude
        db.commit()
        db.refresh(db_address)

    return db_address


def delete_address(db: Session, id: int):
    db.query(models.Address).filter_by(id=id).delete()
    db.commit()
