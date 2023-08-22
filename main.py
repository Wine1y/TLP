from dotenv import load_dotenv
if __name__ == "__main__":
    load_dotenv("config.env")
from os import getenv, path
from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from typing import List, Dict, Any

from core.bot.message_handlers import set_message_handlers
from core.bot.callback_handlers import set_callback_handlers
from core.bot.state_handlers import set_state_handlers
from core.bot.language import BotLanguage, load_languages
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
    languages: Dict[str, BotLanguage]

    def __init__(
        self,
        token: str,
        map_generator: MapGenerator,
        map_renderer: MapRenderer,
        map_seed: int,
        map_size: int,
        section_size: int,
        starting_cords: List[int],
        languages: Dict[str, BotLanguage]
    ):
        self.client = Bot(token=token)
        self.dp = Dispatcher(self.client, storage=MemoryStorage())
        self.map_generator = map_generator
        self.map_renderer = map_renderer
        self.map_seed = map_seed
        self.map_size = map_size
        self.section_size = section_size
        self.bot_map = map_generator.BuildMap(map_seed, map_size, map_size)
        self.languages = languages

        self.starting_cords = self.bot_map.closest_walkable(starting_cords)
        if self.starting_cords is None:
            raise RuntimeError("Can't find any walkable tiles on the map")

        set_message_handlers(self)
        set_callback_handlers(self)
        set_state_handlers(self)
    
    def start_polling(self):
        executor.start_polling(self.dp, skip_updates=True)
    
    def string(self, language: str, string_id: str, **values: Any) -> str:
        return self.languages[language].string(string_id, **values)


if __name__ == "__main__":
    bot = SolarDriveBot(
        token=getenv("BOT_TOKEN"),
        map_generator=PerlinMapGenerator(),
        map_renderer=StaticRenderer(),
        map_seed=123456789,
        map_size=int(getenv("MAP_SIZE")),
        section_size=int(getenv("SECTION_SIZE")),
        starting_cords=[int(cord) for cord in getenv("STARTING_CORDS").split(",")],
        languages=load_languages(path.join("assets", "languages"))
    )
    bot.start_polling()