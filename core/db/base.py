from sqlalchemy import create_engine, Column, Integer, TIMESTAMP
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import scoped_session, sessionmaker
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError
from datetime import datetime
from os import getenv

try:
    DB_PATH = getenv("DATABASE_URL")
    if DB_PATH.startswith("postgres://"):
        DB_PATH = DB_PATH.replace("postgres://", "postgresql://")
    ENGINE = create_engine(DB_PATH)
except AttributeError:
    raise RuntimeError("Can't connect to database! Check db_path!")
BASE = declarative_base()

def get_session():
    return scoped_session(sessionmaker(bind=ENGINE, expire_on_commit=False))

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

        