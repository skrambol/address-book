from sqlalchemy.orm import Session

from . import models, schemas


def get_addresses(db: Session):
    addresses = db.query(models.Address).all()

    return addresses


def create_address(db: Session, address: schemas.AddressCreate):
    new_address = models.Address(**address.model_dump())
    db.add(new_address)
    db.commit()
    db.refresh(new_address)
    return new_address
