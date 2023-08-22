from aiogram import types
from random import randint
from io import BytesIO
from datetime import datetime

from core.db.user import User
from core.bot.markups import get_rover_controller


def set_message_handlers(bot: "SolarDriveBot"):
    
    @bot.dp.message_handler(commands=["map"])
    async def cmd_map(message: types.Message):
        map_image = bot.map_renderer.DrawMap(bot.bot_map, draw_rover=False)
        with BytesIO() as buffer:
            map_image.save(buffer, format="PNG")
            buffer.seek(0)
            await bot.client.send_document(
                caption=f"Текущая игровая карта (seed - {bot.map_seed})",
                chat_id=message.chat.id,
                document=types.InputFile(buffer, filename=f"current_map.png"),
                reply_to_message_id=message.message_id
            )

    @bot.dp.message_handler(commands=["random_map"])
    async def cmd_random_map(message: types.Message):
        seed = randint(0, 999999999)
        build_start = datetime.now()
        random_map = bot.map_generator.BuildMap(seed, bot.map_size, bot.map_size)
        build_time_secs = (datetime.now()-build_start).microseconds/1000000
        render_start = datetime.now()
        map_img = bot.map_renderer.DrawMap(random_map, draw_rover=False)
        render_time_secs = (datetime.now()-render_start).microseconds/1000000
        with BytesIO() as buffer:
            map_img.save(buffer, format="PNG")
            buffer.seek(0)
            await bot.client.send_document(
                caption=f"Генерация всей карты: {round(build_time_secs, 4)} секунд\nРендер всей карты: {round(render_time_secs, 4)} секунд",
                chat_id=message.chat.id,
                document=types.InputFile(buffer, filename=f"map_{seed}.png"),
                reply_to_message_id=message.message_id
            )
    
    @bot.dp.message_handler(commands=["start", "play"])
    async def cmd_start(message: types.Message):
        user = User.get_or_create(message.from_id, bot.starting_cords[0], bot.starting_cords[1])
        if user is None:
            message.reply("К сожалению, произошла ошибка.")
            return
        section_image = bot.map_renderer.DrawMapSubsection(
            bot.bot_map,
            [user.x, user.y],
            bot.section_size,
            bot.section_size
        )
        with BytesIO() as buffer:
            section_image.save(buffer, format="PNG")
            buffer.seek(0)
            await bot.client.send_photo(
                caption=f"X: *{user.x}* Y: *{user.y}*\nЭнергия: *{user.energy}%*",
                chat_id=message.chat.id,
                photo=types.InputFile(buffer, filename=f"{user.x}x{user.y}.png"),
                reply_markup=get_rover_controller(),
                parse_mode="Markdown"
            )

        