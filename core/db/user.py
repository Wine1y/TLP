from sqlalchemy import Column, Integer, String
from typing import Union

from core.db import BaseModel, get_session


class User(BaseModel):
    __tablename__ = "users"

    username = Column(String, nullable=False, unique=True)
    language = Column(String, nullable=False)
    tg_id = Column(Integer, nullable=False, unique=True)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    energy = Column(Integer())

    def __init__(
        self,
        username: str,
        tg_id: int,
        language: str,
        x: int,
        y: int,
        energy:int=100,
    ):
        super().__init__()
        self.username = username
        self.tg_id = tg_id
        self.language = language
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
    def get_by_username(cls, username: str) -> Union["User", None]:
        session = get_session()
        user = session.query(cls).filter(cls.username==username).first()
        if user is not None:
            user.session = session
        return user