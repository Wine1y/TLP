from typing import Optional, List

from core.db import User
from core.db.repository import DatabaseRepository


class UserRepository(DatabaseRepository):
    repository_model=User

    def get_by_tg_id(self, tg_id: int) -> Optional[User]:
        return self.get_first(self.repository_model.tg_id==tg_id)
    
    def get_by_username(self, username: str) -> Optional[User]:
        return self.get_first(self.repository_model.username==username)
    
    def get_by_coordinates(self, x: int, y: int) -> Optional[User]:
        return self.get_first(
            self.repository_model.x==x,
            self.repository_model.y==y
        )
    
    def get_every_in_rectangle(
        self,
        left_top_xy: List[int],
        right_bottom_xy: List[int],
        map_size: int
    ) -> List[User]:
        return self.get_all(
            self._get_rectangle_filter(left_top_xy, right_bottom_xy, map_size)
        )