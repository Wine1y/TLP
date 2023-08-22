
from core.db.base import BASE, ENGINE, BaseModel, get_session
from core.db.user import User
BASE.metadata.create_all(ENGINE)