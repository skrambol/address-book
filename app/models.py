from sqlalchemy import Integer
from sqlalchemy.orm import MappedColumn, mapped_column
from .database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = mapped_column(Integer, primary_key=True)
    name: MappedColumn[str]
    latitude: MappedColumn[float]  # 0 to 90, S-N
    longitude: MappedColumn[float]  # 0 to 180, W-E
