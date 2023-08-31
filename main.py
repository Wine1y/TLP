from dotenv import load_dotenv
if __name__ == "__main__":
    load_dotenv("config.env")
from os import getenv, path


from solar_bot import SolarDriveBot
from core.map_utils.map_generator import PerlinMapGenerator
from core.map_utils.map_renderer import StaticRenderer
from core.bot.language import load_languages

if __name__ == "__main__":
    bot = SolarDriveBot(
        token=getenv("BOT_TOKEN"),
        map_generator=PerlinMapGenerator(),
        map_renderer=StaticRenderer(),
        map_seed=123456789,
        map_size=int(getenv("MAP_SIZE")),
        energy_coefficient=float(getenv("ENERGY_COEFFICIENT")),
        section_size=int(getenv("SECTION_SIZE")),
        starting_cords=[int(cord) for cord in getenv("STARTING_CORDS").split(",")],
        languages=load_languages(path.join("assets", "languages"))
    )
    bot.start_polling()