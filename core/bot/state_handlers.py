from aiogram import types
from aiogram.dispatcher import FSMContext
from io import BytesIO

from core.db.user import User
from core.bot import markups
from core.bot.states import StartingForm


def set_state_handlers(bot: "SolarDriveBot"):
    @bot.dp.message_handler(state=StartingForm.language)
    async def got_language(message: types.Message, state: FSMContext):
        for lang_name, lang in bot.languages.items():
            if lang_name.lower() == message.text.lower():
                await state.update_data(language=lang_name)
                await state.set_state(StartingForm.nickname)
                await bot.client.send_message(
                    message.chat.id,
                    bot.string(lang_name, "select_nick"),
                    reply_markup=markups.nickname_markup(message.from_user.username)
                )
                return
        await bot.client.send_message(
            message.chat.id,
            "Sorry, this language is not supported, try again\n\nК сожалению, этот язык не поддерживается, попробуйте ещё раз",
            reply_markup=markups.languages_markup(bot.languages)
        )
    
    @bot.dp.message_handler(state=StartingForm.nickname)
    async def got_nickname(message: types.Message, state: FSMContext):
        data = await state.get_data()
        user_language = data["language"]
        if len(message.text) > 10:
            await bot.client.send_message(
                message.chat.id,
                bot.string(user_language, "nick_too_long"),
                reply_markup=markups.nickname_markup(message.from_user.username)
            )
            return
        if (nick_owner := User.get_by_username(message.text)) is not None and nick_owner.tg_id != message.from_id:
            await bot.client.send_message(
                message.chat.id,
                bot.string(user_language, "nick_used"),
                reply_markup=markups.nickname_markup(message.from_user.username)
            )
            return
        existing_user = User.get_by_tg_id(message.from_id)
        new_user = None
        if existing_user:
            existing_user.username = message.text
            existing_user.language = user_language
            if existing_user.update():
                new_user = existing_user
        else:
            user = User(
                username=message.text,
                tg_id=message.from_id,
                language=user_language,
                x=bot.starting_cords[0],
                y=bot.starting_cords[1]
            )
            if user.add():
                new_user = user
        if new_user is None:
            await bot.client.send_message(
                message.chat.id,
                bot.string(user_language, "unkown_error")
            )
            return
        await state.finish()
        section_image = bot.map_renderer.DrawMapSubsection(
            bot.bot_map,
            [new_user.x, new_user.y],
            bot.section_size,
            bot.section_size
        )
        with BytesIO() as buffer:
            section_image.save(buffer, format="PNG")
            buffer.seek(0)
            await bot.client.send_photo(
                caption=f"X: *{new_user.x}* Y: *{new_user.y}*\n{bot.string(new_user.language, 'energy')}: *{new_user.energy}%*",
                chat_id=message.chat.id,
                photo=types.InputFile(buffer, filename=f"{new_user.x}x{new_user.y}.png"),
                reply_markup=markups.rover_controller(),
                parse_mode="Markdown"
            )