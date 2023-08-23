from sqlalchemy import Column, Integer, Boolean

from core.db import BaseModel


class SandPile(BaseModel):
    __tablename__ = "sand_piles"
    
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    spawned_naturally = Column(Boolean, default=False)

    def __init__(self, x: int,  y: int, spawned_naturally: bool=False):
        self.x = x
        self.y = y
        self.spawned_naturally = spawned_naturally
        