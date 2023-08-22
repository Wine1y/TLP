from abc import ABC
from PIL import Image, ImageDraw
from typing import List
from os import getenv, path

from core.map_utils.bot_map import BotMap, MapTile



class MapRenderer(ABC):

    def DrawMap(self, bot_map: BotMap, draw_rover: bool=True) -> Image.Image:
        ...

    def DrawMapSubsection(
        self,
        bot_map: BotMap,
        center_cords: List[int],
        section_w: int,
        section_h : int,
        draw_rover: bool=True
    ) -> Image.Image:
        if len(center_cords) != 2:
            raise RuntimeError("Invalid center coordinates, should be [width, height]")
        bbox = self._calc_subsection_bbox(bot_map, center_cords, section_w, section_h)
        return self.DrawMap(
            bot_map.get_subsection(bbox[0], bbox[2], bbox[1], bbox[3]),
            draw_rover
        )
    
    def _calc_subsection_bbox(
        self,
        bot_map: BotMap,
        center_cords: List[int],
        section_w: int,
        section_h : int,
    ):
        if center_cords[0] > bot_map.width or center_cords[1] > bot_map.height:
            raise RuntimeError(
                f"Invalid subsection center ({center_cords[0]}x{center_cords[1]}) for ({bot_map.width}x{bot_map.height}) map"
            )
        if section_w > bot_map.width:
            raise RuntimeError(
                f"Invalid subsection width ({section_w}), map is only {bot_map.width} tiles wide"
            )
        if section_h > bot_map.height:
            raise RuntimeError(
                f"Invalid subsection width ({section_h}), map is only {bot_map.height} tiles tall"
            )
        start_x, start_y = center_cords[0]-section_w//2, center_cords[1]-section_h//2
        end_x, end_y = center_cords[0]+section_w//2, center_cords[1]+section_h//2
        if end_x >= bot_map.width:
            end_x -= bot_map.width
        if end_y >= bot_map.height:
            end_y -= bot_map.height
        return [start_x, start_y, end_x+1, end_y+1]

    
class StaticRenderer(MapRenderer):
    TILE_SIZE = int(getenv("TILE_SIZE"))
    TILE_IMAGES = {
        MapTile.Water: Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (29, 91, 234)),
        MapTile.Sand: Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (255, 213, 123)),
        MapTile.Stone: Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (146, 143, 136)),
        MapTile.Mountains: Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (49, 48, 47)),
    }
    ROVER_IMAGE = Image.open(path.join("assets", "rover.png"))
    
    def DrawMap(self, bot_map: BotMap, draw_rover: bool=True) -> Image.Image:
        image = Image.new("RGBA", (self.TILE_SIZE*bot_map.width, self.TILE_SIZE*bot_map.height))
        for y in range(bot_map.height):
            for x in range(bot_map.width):
                tile_img = self.TILE_IMAGES[bot_map.tile_at(x, y)]
                image.paste(tile_img, (x*self.TILE_SIZE, y*self.TILE_SIZE), tile_img)
        center = (bot_map.width//2, bot_map.height//2)
        if draw_rover:
            image.paste(
                self.ROVER_IMAGE,
                (center[0]*self.TILE_SIZE, center[1]*self.TILE_SIZE),
                self.ROVER_IMAGE
            )
        return image

class StaticDebugRenderer(StaticRenderer):
    def DrawMap(self, bot_map: BotMap, draw_rover: bool=True) -> Image.Image:
        image = super().DrawMap(bot_map, draw_rover)
        draw = ImageDraw.ImageDraw(image)
        for y in range(bot_map.height):
            for x in range(bot_map.width):
                self._draw_coordinates(draw, [x, y], bot_map)
        self._draw_grid(draw, bot_map)
        return image

    def _draw_coordinates(self, draw: ImageDraw.ImageDraw, cords: List[int], bot_map: BotMap):
        draw.text(
            [cords[0]*self.TILE_SIZE+1, cords[1]*self.TILE_SIZE],
            f"{cords[0]+bot_map.start_coordinates[0]},{cords[1]+bot_map.start_coordinates[1]}",
            anchor="la",
            fill=(0, 255, 34)
            )
    
    def _draw_grid(self, draw: ImageDraw.ImageDraw, bot_map: BotMap):
        width, height = bot_map.width*self.TILE_SIZE, bot_map.height*self.TILE_SIZE
        for x in range(0, bot_map.width):
            draw.line([(x*self.TILE_SIZE, 0), (x*self.TILE_SIZE, height)], (255, 0, 0), width=1)
        for y in range(0, bot_map.height):
            draw.line([(0, y*self.TILE_SIZE), (width, y*self.TILE_SIZE)], (255, 0, 0), width=1)