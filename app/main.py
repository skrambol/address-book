from fastapi import Depends, FastAPI
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


@app.get("/")
async def root():
    return {"message": "Hello World"}


@app.get("/addresses/")
async def get_address(db: Session = Depends(get_db)):
    addresses = crud.get_addresses(db)

    return addresses


@app.post("/addresses/")
async def create_address(address: schemas.AddressCreate, db: Session = Depends(get_db)):
    # address = crud.get_address()
    address = crud.create_address(db, address)

    return address
