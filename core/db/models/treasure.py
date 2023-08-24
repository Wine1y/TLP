from sqlalchemy import Column, Integer, ForeignKey
from sqlalchemy.orm import relationship

from core.db import BaseModel


class Treasure(BaseModel):
    __tablename__ = "treasures"

    x = Column(Integer, nullable=False)
    y = Column(Integer, nullable=False)
    sdq_amount = Column(Integer, nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"))
    burried_by = relationship("User", back_populates="treasures")

    def __init__(self, x: int, y: int, sdq_amount: int, owner_id: int):
        self.x = x
        self.y = y
        self.sdq_amount = sdq_amount
        self.user_id = owner_id