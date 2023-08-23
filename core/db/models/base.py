from sqlalchemy import  Column, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime


BASE = declarative_base()

class BaseModel(BASE):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)