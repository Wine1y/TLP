from sqlalchemy import and_, or_
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, ProgrammingError, OperationalError
from abc import ABC
from typing import List, Optional

from core.db import BaseModel , get_session


class DatabaseRepository(ABC):
    session: Session
    repository_model: BaseModel
    
    def __init__(self, session: Optional[Session]=None):
        self.session = session or get_session()

    def add(self, obj: BaseModel) -> bool:
        try:
            self.session.add(obj)
            self.session.commit()
            return True
        except (IntegrityError, ProgrammingError, OperationalError):
            return False
        
    def commit(self) -> bool:
        try:
            self.session.commit()
            return True
        except (IntegrityError, ProgrammingError, OperationalError):
            return False
    
    def get_first(self, *filters: bool) -> Optional[BaseModel]:
        return self.session.query(self.repository_model).filter(*filters).first()
        
    def get_all(self, *filters: bool) -> List[BaseModel]:
        return self.session.query(self.repository_model).filter(*filters).all()
    
    def _get_rectangle_filter(
        self,
        left_top_xy: List[int],
        right_bottom_xy: List[int],
        map_size: int,
    ) -> bool:
        from_x, from_y = left_top_xy[0], left_top_xy[1]
        to_x, to_y = right_bottom_xy[0], right_bottom_xy[1]

        if from_x >= 0 and from_x < to_x:
            x_filter = and_(self.repository_model.x >= from_x, self.repository_model.x < to_x)
        else:
            if from_x < 0:
                from_x=map_size+from_x
            x_filter = or_(self.repository_model.x >= from_x, self.repository_model.x < to_x)
        
        if from_y >= 0 and from_y < to_y:
            y_filter = and_(self.repository_model.y >= from_y, self.repository_model.y < to_y)
        else:
            if from_y < 0:
                from_y = map_size+from_y
            y_filter = or_(self.repository_model.y >= from_y, self.repository_model.y < to_y)
        return and_(x_filter, y_filter)
    
    def __del__(self):
        self.session.close()