from typing import List

from core.db import ChangedTile
from core.db.repository import DatabaseRepository


class ChangedTileRepository(DatabaseRepository):
    repository_model=ChangedTile

    def get_every(self) -> List[ChangedTile]:
        return self.get_all()