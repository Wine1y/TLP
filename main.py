from dotenv import load_dotenv
if __name__ == "__main__":
    load_dotenv("config.env")
from os import getenv
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from typing import List

from core.bot import message_handlers, callback_handlers
from core.map_utils.bot_map import BotMap
from core.map_utils.map_generator import PerlinMapGenerator, MapGenerator
from core.map_utils.map_renderer import MapRenderer, StaticRenderer


class SolarDriveBot():
    client: Bot
    dp: Dispatcher
    map_generator: MapGenerator
    map_renderer: MapRenderer
    map_seed: int
    map_size: int
    starting_cords: List[int]
    bot_map: BotMap

    def __init__(
        self,
        token: str,
        map_generator: MapGenerator,
        map_renderer: MapRenderer,
        map_seed: int,
        map_size: int,
        section_size: int,
        starting_cords: List[int]
    ):
        self.client = Bot(token=token)
        self.dp = Dispatcher(self.client, storage=MemoryStorage())
        self.map_generator = map_generator
        self.map_renderer = map_renderer
        self.map_seed = map_seed
        self.map_size = map_size
        self.section_size = section_size
        self.bot_map = map_generator.BuildMap(map_seed, map_size, map_size)

        self.starting_cords = self.bot_map.closest_walkable(starting_cords)
        if self.starting_cords is None:
            raise RuntimeError("Can't find any walkable tiles on the map")

        message_handlers.set_message_handlers(self)
        callback_handlers.set_callback_handlers(self)
    
    def start_polling(self):
        executor.start_polling(self.dp, skip_updates=True)


if __name__ == "__main__":
    bot = SolarDriveBot(
        getenv("BOT_TOKEN"),
        PerlinMapGenerator(),
        StaticRenderer(),
        123456789,
        int(getenv("MAP_SIZE")),
        int(getenv("SECTION_SIZE")),
        [int(cord) for cord in getenv("STARTING_CORDS").split(",")]
    )
    bot.start_polling()