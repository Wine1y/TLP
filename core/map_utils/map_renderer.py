from abc import ABC
from io import IOBase, BytesIO
from PIL import Image, ImageDraw
from typing import List
from os import getenv, path

from core.map_utils.bot_map import BotMap, MapTile
from core.db import User


class MapRenderer(ABC):

    def DrawMap(self, bot_map: BotMap, draw_players: bool=True) -> Image.Image:
        ...

    def DrawMapSubsection(
        self,
        bot_map: BotMap,
        center_cords: List[int],
        section_w: int,
        section_h : int,
        draw_players: bool=True
    ) -> Image.Image:
        if len(center_cords) != 2:
            raise RuntimeError("Invalid center coordinates, should be [width, height]")
        bbox = bot_map.calc_subsection_bbox(center_cords, section_w, section_h)
        return self.DrawMap(
            bot_map.get_subsection(bbox[0], bbox[2], bbox[1], bbox[3]),
            draw_players
        )
    
    
    def get_image_data(self, image: Image.Image, img_format: str="PNG") -> IOBase:
        buffer = BytesIO()
        image.save(buffer, img_format)
        buffer.seek(0)
        return buffer

    
class StaticRenderer(MapRenderer):
    TILE_SIZE = int(getenv("TILE_SIZE"))
    NICKNAME_MARGIN = -4
    NICKNAME_COLOR = (255, 255, 255)
    TILE_IMAGES = {
        MapTile.Water: Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (29, 91, 234)),
        MapTile.Sand: Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (255, 213, 123)),
        MapTile.Stone: Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (146, 143, 136)),
        MapTile.Mountains: Image.new("RGBA", (TILE_SIZE, TILE_SIZE), (49, 48, 47)),
    }
    ROVER_IMAGE = Image.open(path.join("assets", "rover.png"))
    
    def DrawMap(self, bot_map: BotMap, draw_players: bool=True) -> Image.Image:
        image = Image.new("RGBA", (self.TILE_SIZE*bot_map.width, self.TILE_SIZE*bot_map.height))
        for y in range(bot_map.height):
            for x in range(bot_map.width):
                tile_img = self.TILE_IMAGES[bot_map.tile_at(x, y)]
                image.paste(tile_img, (x*self.TILE_SIZE, y*self.TILE_SIZE), tile_img)
        if draw_players:
            draw = ImageDraw.Draw(image)
            main_map = bot_map.parent_map or bot_map
            left_top_xy = bot_map.start_coordinates
            right_bottom_xy = [
                    bot_map.start_coordinates[0]+bot_map.width,
                    bot_map.start_coordinates[1]+bot_map.height
                ]
            right_bottom_xy = main_map.normalize_cords(right_bottom_xy)
            for user in User.every_in_rectangle(left_top_xy, right_bottom_xy, main_map.width):
                user_cords = [
                    user.x-bot_map.start_coordinates[0],
                    user.y-bot_map.start_coordinates[1]
                ]
                user_cords = main_map.normalize_cords(user_cords)
                self._draw_player(image, draw, user, user_cords)
        return image
    
    def _draw_player(
        self,
        image: Image.Image,
        draw: ImageDraw.ImageDraw,
        user: User,
        user_cords: List[int]
    ) -> None:
        tile_x, tile_y = user_cords[0]*self.TILE_SIZE, user_cords[1]*self.TILE_SIZE
        image.paste(
            self.ROVER_IMAGE,
            (tile_x, tile_y),
            self.ROVER_IMAGE
        )
        text_length = draw.textlength(user.username)
        text_x = tile_x+(self.TILE_SIZE-text_length)//2
        text_y = tile_y+self.TILE_SIZE+self.NICKNAME_MARGIN
        draw.text(
            (text_x, text_y),
            user.username,
            anchor="la",
            fill=self.NICKNAME_COLOR
        )

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
        main_map = bot_map.parent_map or bot_map
        display_cords = main_map.normalize_cords(
            [
                cords[0]+bot_map.start_coordinates[0],
                cords[1]+bot_map.start_coordinates[1]
            ]
        )
        draw.text(
            [cords[0]*self.TILE_SIZE+1, cords[1]*self.TILE_SIZE],
            f"{display_cords[0]},{display_cords[1]}",
            anchor="la",
            fill=(0, 255, 34)
            )
    
    def _draw_grid(self, draw: ImageDraw.ImageDraw, bot_map: BotMap):
        width, height = bot_map.width*self.TILE_SIZE, bot_map.height*self.TILE_SIZE
        for x in range(0, bot_map.width):
            draw.line([(x*self.TILE_SIZE, 0), (x*self.TILE_SIZE, height)], (255, 0, 0), width=1)
        for y in range(0, bot_map.height):
            draw.line([(0, y*self.TILE_SIZE), (width, y*self.TILE_SIZE)], (255, 0, 0), width=1)