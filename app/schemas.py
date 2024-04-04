from pydantic import BaseModel


class AddressBase(BaseModel):
    name: str
    longitude: float
    latitude: float


class Address(AddressBase):
    id: int


class AddressCreate(AddressBase):
    pass

class AddressUpdate(AddressBase):
    pass
