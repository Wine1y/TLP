from typing import List, Optional
from dataclasses import dataclass
from enum import Enum

from core.db import UserRepository


@dataclass
class Tile:
    id: int
    walkable: bool=True
    can_fit_sand_pile: bool=True

class MapTile(Enum):
    Water=Tile(0, walkable=False)
    Sand=Tile(1)
    Stone=Tile(2)
    Mountains=Tile(3, walkable=False, can_fit_sand_pile=False)
    SandPile=Tile(4, walkable=False, can_fit_sand_pile=False)

    @property
    def can_fit_sand_pile(self) -> bool:
        return self.value.can_fit_sand_pile
    
    @property
    def walkable(self) -> bool:
        return self.value.walkable

    @property
    def id(self) -> int:
        return self.value.id

_SAND_PILED_TILES = {
    MapTile.Water: MapTile.Sand,
    MapTile.Sand: MapTile.SandPile,
    MapTile.Stone: MapTile.SandPile,
}

class BotMap():
    parent_map: "BotMap"
    start_coordinates: List[int]
    width: int
    height: int
    tiles: List[List[MapTile]]

    def __init__(
        self,
        tiles: List[List[MapTile]],
        start_coordinates: Optional[List[int]]=None,
        parent_map: Optional["BotMap"]=None
    ):
        self.tiles = tiles
        self.height = len(self.tiles)
        self.width = len(self.tiles[0]) if self.height > 0 else 0
        self.start_coordinates = start_coordinates if start_coordinates is not None else [0, 0]
        self.parent_map = parent_map

    def calc_subsection_bbox(
        self,
        center_cords: List[int],
        section_w: int,
        section_h : int,
    ):
        if center_cords[0] > self.width or center_cords[1] > self.height:
            raise RuntimeError(
                f"Invalid subsection center ({center_cords[0]}x{center_cords[1]}) for ({self.width}x{self.height}) map"
            )
        if section_w > self.width:
            raise RuntimeError(
                f"Invalid subsection width ({section_w}), map is only {self.width} tiles wide"
            )
        if section_h > self.height:
            raise RuntimeError(
                f"Invalid subsection width ({section_h}), map is only {self.height} tiles tall"
            )
        start_x, start_y = center_cords[0]-section_w//2, center_cords[1]-section_h//2
        end_x, end_y = center_cords[0]+section_w//2, center_cords[1]+section_h//2
        if end_x >= self.width:
            end_x -= self.width
        if end_y >= self.height:
            end_y -= self.height
        return [start_x, start_y, end_x+1, end_y+1]

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
        return BotMap(section_tiles, start_coordinates=[from_x, from_y], parent_map=self)
    
    def tile_at(self, x: int, y: int) -> MapTile:
        if x >= self.width or y >= self.height:
            raise RuntimeError(f"Invalid coordinates ({x}x{y}), for {self.width}x{self.height} map")
        return self.tiles[y][x]
    
    def set_tile_at(self, x: int, y: int, tile: MapTile) -> None:
        if x >= self.width or y >= self.height:
            raise RuntimeError(f"Invalid coordinates ({x}x{y}), for {self.width}x{self.height} map")
        self.tiles[y][x] = tile
    
    def closest_walkable(self, cords: List[int]) -> Optional[List[int]]:
        if self.tile_at(cords[0], cords[1]).walkable:
            return cords
        max_radius = max(self.width-cords[0], self.height-cords[1])
        rep = UserRepository()
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
                if not self.is_walkable(sibling_cords[0], sibling_cords[1], rep):
                    continue
                return sibling_cords
        return None
    
    def is_walkable(self, x: int, y: int, user_rep: UserRepository) -> bool:
        return self.tile_at(x, y).walkable and user_rep.get_by_coordinates(x, y) is None
    
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

def put_sand_pile(tile: MapTile) -> MapTile:
    return MapTile(_SAND_PILED_TILES[tile])