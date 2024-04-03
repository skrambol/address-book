from sqlalchemy import Column, Float, Integer, String
from .database import Base


class Address(Base):
    __tablename__ = "addresses"

    id = Column(Integer, primary_key=True)
    name = Column(String, index=True)
    longitude = Column(Float)  # 0 to 180, W-E
    latitude = Column(Float)  # 0 to 90, S-N
