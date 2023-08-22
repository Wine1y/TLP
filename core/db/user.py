from sqlalchemy import Column, Integer
from typing import Union

from core.db import BaseModel, get_session


class User(BaseModel):
    __tablename__ = "users"

    tg_id = Column(Integer, nullable=False, unique=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    energy = Column(Integer())

    def __init__(self, tg_id: int, x: int, y: int, energy:int=100):
        super().__init__()
        self.tg_id = tg_id
        self.x = x
        self.y = y
        self.energy = energy

    @classmethod
    def get_by_tg_id(cls, tg_id: int) -> Union["User", None]:
        session = get_session()
        user = session.query(cls).filter(cls.tg_id==tg_id).first()
        if user is not None:
            user.session = session
        return user
    
    @classmethod
    def get_or_create(cls, tg_id: int, default_x: int, default_y: int) -> Union["User", None]:
        user = cls.get_by_tg_id(tg_id)
        if user is not None:
            return user
        cls(tg_id, default_x, default_y).add()
        return cls.get_by_tg_id(tg_id)