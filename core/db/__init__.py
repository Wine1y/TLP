from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from os import getenv


try:
    DB_PATH = getenv("DATABASE_URL")
    if DB_PATH.startswith("postgres://"):
        DB_PATH = DB_PATH.replace("postgres://", "postgresql://")
    ENGINE = create_engine(DB_PATH)
except AttributeError:
    raise RuntimeError(f"Can't connect to database! Check db_path!")

def get_session():
    return scoped_session(sessionmaker(bind=ENGINE, expire_on_commit=False))

from core.db.base import BASE, BaseModel
from core.db.user import User