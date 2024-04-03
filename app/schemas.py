from pydantic import BaseModel, ConfigDict


class AddressBase(BaseModel):
    name: str
    longitude: float
    latitude: float


class Address(AddressBase):
    model_config = ConfigDict(from_attributes=True)
    id: int


class AddressCreate(AddressBase):
    pass
