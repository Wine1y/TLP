from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

@dataclass
class Tile:
    id: int
    walkable: bool=True

class MapTile(Enum):
    Water=Tile(0, walkable=False)
    Sand=Tile(1)
    Stone=Tile(2)
    Mountains=Tile(3, walkable=False)

class BotMap():
    start_coordinates: List[int]
    width: int
    height: int
    tiles: List[List[MapTile]]

    def __init__(
        self,
        tiles: List[List[MapTile]],
        start_coordinates: Optional[List[int]]=None
    ):
        self.tiles = tiles
        self.height = len(self.tiles)
        self.width = len(self.tiles[0]) if self.height > 0 else 0
        self.start_coordinates = start_coordinates if start_coordinates is not None else [0, 0]
    
    def get_subsection(
        self,
        from_x: int,
        to_x: int,
        from_y: int,
        to_y: int
    ) -> "BotMap":
        if from_y >= 0 and from_y < to_y:
            rows = self.tiles[from_y:to_y]
        else:
            rows = self.tiles[from_y:]+self.tiles[:to_y]
        section_tiles = [
            row[from_x:to_x] if from_x >= 0 and from_x < to_x else row[from_x:]+row[:to_x]
            for row in rows
        ]
        return BotMap(section_tiles, start_coordinates=[from_x, from_y])
    
    def tile_at(self, x: int, y: int) -> MapTile:
        if x >= self.width or y >= self.height:
            raise RuntimeError(f"Invalid coordinates ({x}x{y}), for {self.width}x{self.height} map")
        return self.tiles[y][x]
    
    def closest_walkable(self, cords: List[int]) -> Optional[List[int]]:
        if self.tile_at(cords[0], cords[1]).value.walkable:
            return cords
        max_radius = max(self.width-cords[0], self.height-cords[1])
        for radius in range(1, max_radius):
            closest_siblings = [
                (cords[0]-radius, cords[1]),        #L
                (cords[0]+radius, cords[1]),        #R
                (cords[0], cords[1]-radius),        #T
                (cords[0], cords[1]+radius),        #B
                (cords[0]-radius, cords[1]-radius), #LT
                (cords[0]+radius, cords[1]-radius), #RT
                (cords[0]+radius, cords[1]+radius), #RB
                (cords[0]-radius, cords[1]+radius)  #LB
            ]
            for sibling_cords in closest_siblings:
                if abs(sibling_cords[0]) > self.width or abs(sibling_cords[1]) > self.height:
                    continue
                if self.tile_at(sibling_cords[0], sibling_cords[1]).value.walkable:
                    return sibling_cords
        return None
    
    def normalize_cords(self, cords: List[int]) -> List[int]:
        x, y = cords[0], cords[1]
        if x < 0:
            x+=self.width
        if x >= self.width:
            x-= self.width
        if y < 0:
            y+=self.height
        if y >= self.height:
            y-=self.height
        return [x, y]