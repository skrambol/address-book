from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from loguru import logger

from app import crud, models, schemas
from app.database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/addresses/", response_model=list[schemas.Address])
def get_addresses(
    lat: float | None = schemas.LatitudeQuery,
    long: float | None = schemas.LongitudeQuery,
    distance: float | None = schemas.DistanceQuery,
    db: Session = Depends(get_db),
):
    """
    get all addresses

    if no query params are given, all addresses will be listed

    all query params (lat, long, distance) must be provided to filter out the results
    """
    if all(param is None for param in [lat, long, distance]):
        return db.query(models.Address).all()

    # elif all(param is not None for param in [lat, long, distance]): # mypy sees this as an error
    elif lat is not None and long is not None and distance is not None:
        addresses = crud.get_addresses_in_radius(db, (lat, long), distance)
        return addresses

    else:
        raise HTTPException(
            status_code=422,
            detail="lat, long, or distance is missing from query params",
        )


@app.post(
    "/addresses/",
    responses={400: {"description": "Duplicate Coordinates"}},
    response_model=schemas.Address,
)
def create_address(address: schemas.AddressCreate, db: Session = Depends(get_db)):
    """
    adds a new address entry from the given details.

    returns the newly added address

    returns an error if there is a duplicate address from the input coordinates
    """
    try:
        logger.debug(address)
        return crud.create_address(db, address)
    except IntegrityError as e:
        if "UNIQUE" in str(e):  # if unique constraint
            raise HTTPException(status_code=400, detail="duplicate coordinates")

        # re-raise all other integrity errors
        raise e


@app.put(
    "/addresses/{id}",
    responses={
        400: {"description": "Duplicate Coordinates"},
        404: {"description": "Address with ID Does Not Exist"},
    },
    response_model=schemas.Address,
)
def update_address(
    id: int, address: schemas.AddressUpdate, db: Session = Depends(get_db)
):
    """
    updates the details of the address with the given ID

    returns the updated details of the address

    returns an error if there is no address with the given ID
    """
    try:
        logger.debug(address)
        db_address = crud.update_address(db, id, address)

        if not db_address:
            raise HTTPException(status_code=404, detail="id not found")

        return db_address
    except IntegrityError as e:
        if "UNIQUE" in str(e):  # if unique constraint
            raise HTTPException(status_code=400, detail="duplicate coordinates")

        # re-raise all other integrity errors
        raise e


@app.delete("/addresses/{id}", status_code=204)
def delete_address(id: int, db: Session = Depends(get_db)):
    """
    deletes the address with the given ID

    returns None
    """
    crud.delete_address(db, id)
    return None
