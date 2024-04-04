from fastapi import Depends, FastAPI, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError

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
    try:
        return crud.create_address(db, address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="duplicate coordinates")


@app.put("/addresses/{id}")
async def update_address(
    id: int, address: schemas.AddressUpdate, db: Session = Depends(get_db)
):
    try:
        return crud.update_address(db, id, address)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except IntegrityError as e:
        raise HTTPException(status_code=400, detail="duplicate coordinates")
