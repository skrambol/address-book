from pydantic import BaseModel


class AddressBase(BaseModel):
    name: str
    longitude: float
    latitude: float


class Address(AddressBase):
    id: int

    class Config:
        from_attributes = True


class AddressCreate(AddressBase):
    pass
