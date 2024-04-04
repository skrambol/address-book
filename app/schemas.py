from fastapi import Query
from pydantic import BaseModel


LatitudeQuery = Query(
    default=None,
    description="latitude in degrees. can go from -90.0 to 90.0 where negative values denotes south",
    ge=-90.0,
    le=90.0,
)
LongitudeQuery = Query(
    default=None,
    description="longitude in degrees. can go from -180.0 to 180.0 where negative values denotes west",
    ge=-180.0,
    le=180.0,
)
DistanceQuery = Query(
    default=None,
    description="distance in kilometers",
    ge=0.0,
)


class AddressBase(BaseModel):
    name: str = Query(description="name of the location of the given coordinates")
    latitude: float = LatitudeQuery
    longitude: float = LongitudeQuery


class Address(AddressBase):
    id: int


class AddressCreate(AddressBase):
    pass


class AddressUpdate(AddressBase):
    pass
