from sqlalchemy import create_engine
from sqlalchemy.orm import scoped_session, sessionmaker
from os import getenv


try:
    DB_PATH = getenv("DATABASE_URL")
    if DB_PATH.startswith("postgres://"):
        DB_PATH = DB_PATH.replace("postgres://", "postgresql://")
    ENGINE = create_engine(DB_PATH)
except AttributeError:
    raise RuntimeError("Can't connect to database! Check db_path!")

def get_session():
    return scoped_session(sessionmaker(bind=ENGINE, expire_on_commit=False))

from core.db.models.base import BASE, BaseModel
from core.db.models.user import User
from core.db.models.changed_tile import ChangedTile
from core.db.repositories.user import UserRepository
from core.db.repositories.changed_tile import ChangedTileRepository