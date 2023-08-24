from typing import Optional

from core.db import Treasure
from core.db.repository import DatabaseRepository


class TreasureRepository(DatabaseRepository):
    repository_model=Treasure

    def get_by_coordinates(self, x: int, y: int) -> Optional[Treasure]:
        return self.get_first(
            self.repository_model.x==x,
            self.repository_model.y==y
        )