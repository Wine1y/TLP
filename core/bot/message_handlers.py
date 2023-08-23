from aiogram import types
from aiogram.dispatcher import FSMContext
from random import randint

from core.db import UserRepository
from core.bot import markups, states


def set_message_handlers(bot: "SolarDriveBot"):
    
    @bot.dp.message_handler(commands=["map"])
    async def cmd_map(message: types.Message):
        rep = UserRepository()
        user = rep.get_by_tg_id(message.from_id)
        if user is None:
            await message.reply(bot.string("English", "no_user_error"))
            return
        map_image = bot.map_renderer.DrawMap(bot.bot_map, draw_players=False)
        with bot.map_renderer.get_image_data(map_image) as image_data:
            await bot.client.send_document(
                caption=bot.string(user.language, "current_map_seed", seed=bot.map_seed),
                chat_id=message.chat.id,
                document=types.InputFile(image_data, filename="current_map.png"),
                reply_to_message_id=message.message_id
            )
            

    @bot.dp.message_handler(commands=["random_map"])
    async def cmd_random_map(message: types.Message):
        seed = randint(0, 999999999)
        random_map = bot.map_generator.BuildMap(seed, bot.map_size, bot.map_size)
        map_img = bot.map_renderer.DrawMap(random_map, draw_players=False)
        with bot.map_renderer.get_image_data(map_img) as image_data: 
            await bot.client.send_document(
                chat_id=message.chat.id,
                document=types.InputFile(image_data, filename=f"map_{seed}.png"),
                reply_to_message_id=message.message_id
            )
    
    @bot.dp.message_handler(commands=["play"])
    async def cmd_play(message: types.Message):
        rep = UserRepository()
        user = rep.get_by_tg_id(message.from_id)
        if user is None:
            await message.reply(bot.string("English", "no_user_error"))
            return
        section_image = bot.user_subsection(user)
        with bot.map_renderer.get_image_data(section_image) as image_data:
            await bot.client.send_photo(
                caption=bot.user_controller_info(user),
                chat_id=message.chat.id,
                photo=types.InputFile(image_data, filename=f"{user.x}x{user.y}.png"),
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
        await state.set_state(states.StartingForm.language)
    
    @bot.dp.message_handler(commands=["tp"])
    async def cmd_teleport(message: types.Message):
        args = message.text.split(" ")
        usage = "Использование: /tp (nickname) (new x coordinate) (new y coordinate)"
        if len(args) != 4:
            await message.reply(usage)
            return
        try:
            x = int(args[2])
            y = int(args[3])
        except ValueError:
            await message.reply(usage)
            return
        if x >= bot.map_size or y >= bot.map_size or x < 0 or y < 0:
            await message.reply("Координаты невалидны")
            return
        rep = UserRepository()
        user = rep.get_by_username(args[1])
        if user is None:
            await message.reply("Пользователь не найден")
            return
        user.x = x
        user.y = y
        if not rep.commit():
            await message.reply("Неизвестная ошибка")
        await message.reply(f"Пользователь {args[1]} телепортирован")
        
        