from typing import List

from core.db import SandPile
from core.db.repository import DatabaseRepository


class SandPileRepository(DatabaseRepository):
    repository_model=SandPile

    def get_every(self) -> List[SandPile]:
        return self.get_all()
    
    def get_every_in_rectangle(
        self,
        left_top_xy: List[int],
        right_bottom_xy: List[int],
        map_size: int
    ) -> List[SandPile]:
        return self.get_all(
            self._get_rectangle_filter(left_top_xy, right_bottom_xy, map_size)
        )