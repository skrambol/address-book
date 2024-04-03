from sqlalchemy.orm import Session

from . import models, schemas


def get_address_by_coordinates(db: Session, latitude: float, longitude: float):
    address = (
        db.query(models.Address)
        .filter(
            models.Address.latitude == latitude, models.Address.longitude == longitude
        )
        .first()
    )

    return address


def get_addresses(db: Session):
    addresses = db.query(models.Address).all()

    return addresses


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
