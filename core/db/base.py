from sqlalchemy import  Column, Integer, TIMESTAMP
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

from core.db import get_session

BASE = declarative_base()


class BaseModel(BASE):
    __abstract__ = True

    id = Column(Integer, nullable=False, unique=True, primary_key=True, autoincrement=True)
    created = Column(TIMESTAMP, nullable=False, default=datetime.utcnow)

    def __init__(self):
        self.session = get_session()

    def add(self) -> bool:
        if self.id is not None:
            raise RuntimeError(f"{self.__class__.__name__} already exists with id {self.id}")
        try:
            self.session.add(self)
            self.session.commit()
            return True
        except (IntegrityError, ProgrammingError, OperationalError) as e:
            return False
        
    def update(self) -> bool:
        if self.id is None:
            raise RuntimeError("Can't updated detached model")
        try:
            self.session.commit()
            return True
        except (IntegrityError, ProgrammingError, OperationalError):
            return False

        