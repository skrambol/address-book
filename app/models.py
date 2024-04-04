from sqlalchemy import Integer
from sqlalchemy.orm import MappedColumn, mapped_column
from .database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = mapped_column(Integer, primary_key=True)
    name: MappedColumn[str]
    latitude: MappedColumn[float]  # 0 to 90, S-N
    longitude: MappedColumn[float]  # 0 to 180, W-E

    @staticmethod
    def is_valid_latitude(lat: float):
        return -90.0 <= lat <= 90.0

    @staticmethod
    def is_valid_longitude(long: float):
        return -180.0 <= long <= 180.0
