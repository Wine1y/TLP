from sqlalchemy import Column, Integer, String

from core.db import BaseModel


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, nullable=False, unique=True)
    language = Column(String, nullable=False)
    tg_id = Column(Integer, nullable=False, unique=True)
    sqd_msg_id = Column(Integer, nullable=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    energy = Column(Integer)

    def __init__(
        self,
        username: str,
        tg_id: int,
        language: str,
        x: int,
        y: int,
        energy:int=100,
    ):
        self.username = username
        self.tg_id = tg_id
        self.sqd_msg_id=None
        self.language = language
        self.x = x
        self.y = y
        self.energy = energy