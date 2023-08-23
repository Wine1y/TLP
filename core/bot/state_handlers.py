from aiogram import types
from aiogram.dispatcher import FSMContext

from core.db import User, UserRepository
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
        rep = UserRepository()
        if (nick_owner := rep.get_by_username(message.text)) is not None and nick_owner.tg_id != message.from_id:
            await bot.client.send_message(
                message.chat.id,
                bot.string(user_language, "nick_used"),
                reply_markup=markups.nickname_markup(message.from_user.username)
            )
            return
        existing_user = rep.get_by_tg_id(message.from_id)
        new_user = None
        if existing_user is not None:
            existing_user.username = message.text
            existing_user.language = user_language
            if rep.commit():
                new_user = existing_user
        else:
            user = User(
                username=message.text,
                tg_id=message.from_id,
                language=user_language,
                x=bot.starting_cords[0],
                y=bot.starting_cords[1]
            )
            if rep.add(user):
                new_user = rep.get_by_tg_id(message.from_id)
        if new_user is None:
            await bot.client.send_message(
                message.chat.id,
                bot.string(user_language, "unkown_error")
            )
            return
        await state.finish()
        await bot.client.send_message(
            message.chat.id,
            bot.string(user_language, "successful_sign_up"),
            reply_markup=markups.remove_keyboard())
        sqd_msg = await bot.client.send_message(
            message.chat.id,
            bot.string(user_language, "sqd_msg", balance=100),
            reply_markup=markups.sqd_msg_markup(bot.languages[user_language])
        )
        if new_user.sqd_msg_id is not None:
            await bot.client.unpin_chat_message(message.chat.id, new_user.sqd_msg_id)
        await sqd_msg.pin()
        new_user.sqd_msg_id = sqd_msg.message_id
        rep.commit()
        section_image = bot.user_subsection(new_user)
        with bot.map_renderer.get_image_data(section_image) as image_data:
            await bot.client.send_photo(
                caption=bot.user_controller_info(new_user),
                chat_id=message.chat.id,
                photo=types.InputFile(image_data, filename=f"{new_user.x}x{new_user.y}.png"),
                reply_markup=markups.rover_controller(),
                parse_mode="Markdown"
            )