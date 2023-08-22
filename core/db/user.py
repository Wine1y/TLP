from sqlalchemy import Column, Integer, String, and_, or_
from typing import Optional, List

from core.db import BaseModel, get_session

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
        super().__init__()
        self.username = username
        self.tg_id = tg_id
        self.sqd_msg_id=None
        self.language = language
        self.x = x
        self.y = y
        self.energy = energy

    @classmethod
    def get_by_tg_id(cls, tg_id: int) -> Optional["User"]:
        session = get_session()
        user = session.query(cls).filter(cls.tg_id==tg_id).first()
        if user is not None:
            user.session = session
        return user

    @classmethod
    def get_by_username(cls, username: str) -> Optional["User"]:
        session = get_session()
        user = session.query(cls).filter(cls.username==username).first()
        if user is not None:
            user.session = session
        return user
    
    @classmethod
    def get_by_coordinates(cls, x: int, y: int) -> Optional["User"]:
        session = get_session()
        user = session.query(cls).filter(cls.x==x, cls.y==y).first()
        if user is not None:
            user.session = session
        return user

    @classmethod
    def every_in_rectangle(
        cls,
        left_top_xy: List[int],
        right_bottom_xy: List[int],
        map_size: int
    ) -> List["User"]:
        from_x, from_y = left_top_xy[0], left_top_xy[1]
        to_x, to_y = right_bottom_xy[0], right_bottom_xy[1]

        if from_x >= 0 and from_x < to_x:
            x_filter = and_(cls.x >= from_x, cls.x < to_x)
        else:
            if from_x < 0:
                from_x=map_size+from_x
            x_filter = or_(cls.x >= from_x, cls.x < to_x)
        
        if from_y >= 0 and from_y < to_y:
            y_filter = and_(cls.y >= from_y, cls.y < to_y)
        else:
            if from_y < 0:
                from_y = map_size+from_y
            y_filter = or_(cls.y >= from_y, cls.y < to_y)
        session = get_session()
        users = session.query(cls).filter(
            x_filter, y_filter
        ).all()
        for user in users:
            user.session = session
        return users