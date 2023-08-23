from sqlalchemy import Column, Integer, Boolean

from core.db import BaseModel


class ChangedTile(BaseModel):
    __tablename__ = "changed_tiles"
    
    tile_id = Column(Integer, nullable=False)
    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    spawned_naturally = Column(Boolean, default=False)

    def __init__(self, tile_id: int, x: int,  y: int, spawned_naturally: bool=False):
        self.tile_id = tile_id
        self.x = x
        self.y = y
        self.spawned_naturally = spawned_naturally
        