from sqlalchemy import Column, Integer, String, Float
from sqlalchemy.orm import relationship

from core.db import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, nullable=False, unique=True)
    language = Column(String, nullable=False)
    tg_id = Column(Integer, nullable=False, unique=True)
    sdq_msg_id = Column(Integer, nullable=True)
    playground_msg_id = Column(Integer, nullable=True)
    last_energy_refresh = Column(Integer, nullable=True)
    sdq_balance = Column(Integer, default=100)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    energy = Column(Float)
    treasures = relationship("Treasure", back_populates="buried_by")

    def __init__(
        self,
        username: str,
        tg_id: int,
        language: str,
        x: int,
        y: int,
        sdq_balance: int,
        energy:int=100,
    ):
        self.username = username
        self.tg_id = tg_id
        self.sqd_msg_id = None
        self.playground_msg_id = None
        self.last_energy_refresh = None
        self.sqd_balance = sdq_balance
        self.language = language
        self.x = x
        self.y = y
        self.energy = energy