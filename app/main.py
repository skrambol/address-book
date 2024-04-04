from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from . import crud, models, schemas
from .database import SessionLocal, engine

models.Base.metadata.create_all(bind=engine)

app = FastAPI()


def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


@app.get("/addresses/")
async def get_address_in_radius(
    lat: float, long: float, distance: float, db: Session = Depends(get_db)
):
    try:
        addresses = crud.get_addresses_in_radius(db, (lat, long), distance)
        return addresses

    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))


@app.post("/addresses/")
async def create_address(address: schemas.AddressCreate, db: Session = Depends(get_db)):
    db_address = crud.get_address_by_coordinates(
        db, address.latitude, address.longitude
    )
    if db_address:
        raise HTTPException(status_code=400, detail="duplicate coordinates")

    try:
        return crud.create_address(db, address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
