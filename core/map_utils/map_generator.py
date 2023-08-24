from abc import ABC
from perlin_noise import PerlinNoise
from typing import List
from random import sample

from core.map_utils.bot_map import BotMap, MapTile
from core.db import ChangedTileRepository, UserRepository, ChangedTile


_PERLIN_OCTAVES = [6, 12]
_OCTAVE_STEP = 0.5
_EDGE_LENGTH=5
_TILES_MAX_PERLIN_VALUE = [
    (MapTile.Water, -0.3),
    (MapTile.Sand, -0.08),
    (MapTile.Stone, 0.28),
    (MapTile.Mountains, None)
]
_NATURAL_SAND_PILES_COEFFICIENT = 0.33

class MapGenerator(ABC):
    def BuildMap(
        self,
        seed: int,
        map_w: int,
        map_h: int,
        add_changed_tiles: bool=True
    ) -> BotMap:
        ...

def linspace(start: float, end: float, length: int) -> List[float]:
    length+=1
    h = (end-start)/(length-1)
    return [start+h*i for i in range(length)][:-1]

class PerlinMapGenerator(MapGenerator):
    def BuildMap(
        self,
        seed: int,
        map_w: int,
        map_h: int,
        add_changed_tiles: bool=True
    ) -> BotMap:
        perlins = [PerlinNoise(octave, seed) for octave in _PERLIN_OCTAVES]
        noise = [
            [
                self._get_noises_val(perlins, [i/map_w, j/map_h])*-1
                for j in range(map_w)
            ]
            for i in range(map_h)
        ]
        noise = self._merge_edges(noise)
        bot_map = self._noise_to_map(noise)
        if add_changed_tiles:
            bot_map = self._place_changed_tiles(bot_map)
        return bot_map
    
    def _get_noises_val(self, perlins: List[PerlinNoise], cords: List[int]) -> float:
        return sum([
            perlins[i].noise(cords)*pow(_OCTAVE_STEP, i)
            for i in range(len(perlins))
        ])
        
    def _noise_to_map(self, noise: List[List[float]]) -> BotMap:
        tiles = [
            [
                self._perlin_to_tile(value)
                for value in row
            ]
            for row in noise
        ]
        return BotMap(tiles)

    def _perlin_to_tile(self, perlin_value: float) -> MapTile:
        for tile_data in _TILES_MAX_PERLIN_VALUE:
            if tile_data[1] is None or perlin_value < tile_data[1]:
                return tile_data[0]
    
    def _merge_edges(self, noise: List[List[float]]) -> List[List[float]]:

        bottom_edge = [
            linspace(noise[0][x], noise[len(noise)-_EDGE_LENGTH+1][x], _EDGE_LENGTH)
            for x in range(len(noise[0]))
        ]
        right_edge = [
            linspace(noise[y][0], noise[y][len(noise[y])-_EDGE_LENGTH+1], _EDGE_LENGTH)
            for y in range(len(noise))
        ]

        for edge_offset in range(_EDGE_LENGTH):
            bottom_line = [bottom_edge[x][edge_offset] for x in range(len(noise[0]))]
            right_line = [right_edge[y][edge_offset] for y in range(len(noise))]
            noise[len(noise)-1-edge_offset] = bottom_line
            for y in range(len(noise)):
                noise[y][len(noise[y])-1-edge_offset] = right_line[y]
        return noise
    
    def _place_changed_tiles(self, bot_map: BotMap) -> BotMap:
        registered_tiles = list(MapTile)
        tiles_rep, user_rep = ChangedTileRepository(), UserRepository()
        tiles = tiles_rep.get_every()
        natural_piles_required = round(bot_map.width*_NATURAL_SAND_PILES_COEFFICIENT)
        for tile in tiles:
            if tile.tile_id==MapTile.SandPile.id and tile.spawned_naturally:
                natural_piles_required-=1
            bot_map.set_tile_at(tile.x, tile.y, registered_tiles[tile.tile_id])
        if natural_piles_required > 0:
            available_coords = [
                (x,y)
                for x in range(bot_map.width)
                for y in range(bot_map.height)
                if bot_map.is_walkable(x, y, user_rep)
            ]
            for new_pile_cords in sample(available_coords, natural_piles_required):
                bot_map.set_changed_tile_at(
                    new_pile_cords[0],
                    new_pile_cords[1],
                    MapTile.SandPile,
                    tiles_rep,
                    spawned_naturally=True
                )
        return bot_map
        