from sqlalchemy import Integer, UniqueConstraint
from sqlalchemy.orm import MappedColumn, mapped_column
from .database import Base


class Address(Base):
    __tablename__ = "addresses"
    __table_args__ = (
        UniqueConstraint("latitude", "longitude", name="unique_coordinates"),
        # probably not needed since there is application-level validation
        # CheckConstraint("latitude >= -90.0 and latitude <= 90.0", name="valid_latitude"),
        # CheckConstraint("longitude >= -180.0 and longitude <= 180.0", name="valid_longitude"),
    )

    id = mapped_column(Integer, primary_key=True)
    name: MappedColumn[str]
    latitude: MappedColumn[float]  # 0 to 90, S-N
    longitude: MappedColumn[float]  # 0 to 180, W-E
