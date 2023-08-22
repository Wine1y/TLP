from aiogram import types
from aiogram.dispatcher import FSMContext
from random import randint
from io import BytesIO

from core.db.user import User
from core.bot import markups
from core.bot.states import StartingForm


def set_message_handlers(bot: "SolarDriveBot"):
    
    @bot.dp.message_handler(commands=["map"])
    async def cmd_map(message: types.Message):
        user = User.get_by_tg_id(message.from_id)
        if user is None:
            await message.reply(bot.string("English", "unkown_error"))
            return
        map_image = bot.map_renderer.DrawMap(bot.bot_map, draw_rover=False)
        with BytesIO() as buffer:
            map_image.save(buffer, format="PNG")
            buffer.seek(0)
            await bot.client.send_document(
                caption=bot.string(user.language, "current_map_seed", seed=bot.map_seed),
                chat_id=message.chat.id,
                document=types.InputFile(buffer, filename="current_map.png"),
                reply_to_message_id=message.message_id
            )

    @bot.dp.message_handler(commands=["random_map"])
    async def cmd_random_map(message: types.Message):
        seed = randint(0, 999999999)
        random_map = bot.map_generator.BuildMap(seed, bot.map_size, bot.map_size)
        map_img = bot.map_renderer.DrawMap(random_map, draw_rover=False)
        with BytesIO() as buffer:
            map_img.save(buffer, format="PNG")
            buffer.seek(0)
            await bot.client.send_document(
                chat_id=message.chat.id,
                document=types.InputFile(buffer, filename=f"map_{seed}.png"),
                reply_to_message_id=message.message_id
            )
    
    @bot.dp.message_handler(commands=["play"])
    async def cmd_play(message: types.Message):
        user = User.get_by_tg_id(message.from_id)
        if user is None:
            await message.reply(bot.string("English", "unkown_error"))
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
                caption=f"X: *{user.x}* Y: *{user.y}*\n{bot.string(user.language, 'energy')}: *{user.energy}%*",
                chat_id=message.chat.id,
                photo=types.InputFile(buffer, filename=f"{user.x}x{user.y}.png"),
                reply_markup=markups.rover_controller(),
                parse_mode="Markdown"
            )
    
    @bot.dp.message_handler(commands=["start"])
    async def cmd_start(message: types.Message, state: FSMContext):
        await bot.client.send_message(
            message.chat.id,
            "Please, set a language\n\nПожалуйста, выберите язык",
            reply_markup=markups.languages_markup(bot.languages)
        )
        await state.set_state(StartingForm.language)