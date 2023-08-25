from aiogram import types
from aiogram.dispatcher import FSMContext
from os import getenv

from core.db import User, Treasure, UserRepository, TreasureRepository
from core.bot import markups, states


def set_state_handlers(bot: "SolarDriveBot"):
    @bot.dp.message_handler(state=states.StartingForm.language)
    async def got_language(message: types.Message, state: FSMContext):
        for lang_name, lang in bot.languages.items():
            if lang_name.lower() == message.text.lower():
                await state.update_data(language=lang_name)
                await state.set_state(states.StartingForm.nickname)
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
    
    @bot.dp.message_handler(state=states.StartingForm.nickname)
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
            existing_user.sdq_balance = existing_user.sdq_balance or int(getenv("STARTING_BALANCE"))
            if rep.commit():
                new_user = existing_user
        else:
            starting_cords = bot.bot_map.closest_walkable(bot.starting_cords)
            user = User(
                username=message.text,
                tg_id=message.from_id,
                language=user_language,
                x=starting_cords[0],
                y=starting_cords[1],
                sdq_balance=int(getenv("STARTING_BALANCE"))
            )
            if rep.add(user):
                new_user = rep.get_by_tg_id(message.from_id)
        if new_user is None:
            await bot.client.send_message(
                message.chat.id,
                bot.string(user_language, "unknown_error")
            )
            return
        await state.finish()
        await bot.client.send_message(
            message.chat.id,
            bot.string(user_language, "successful_sign_up"),
            reply_markup=markups.remove_keyboard())
        sdq_msg = await bot.client.send_message(
            message.chat.id,
            bot.string(user_language, "sdq_msg", balance=new_user.sdq_balance),
            reply_markup=markups.sqd_msg_markup(bot.languages[user_language])
        )
        await sdq_msg.pin()
        if new_user.sdq_msg_id is not None:
            await bot.client.unpin_chat_message(message.chat.id, new_user.sdq_msg_id)
        new_user.sdq_msg_id = sdq_msg.message_id
        rep.commit()
        await bot.send_playground_message(new_user, message.chat.id, rep)
    
    @bot.dp.message_handler(state=states.TreasureBuryForm.amount)
    async def got_amount(message: types.Message, state: FSMContext):
        user_rep = UserRepository()
        user = user_rep.get_by_tg_id(message.from_id)
        if user is None:
            await bot.client.send_message(
                message.chat.id,
                bot.string("English", "no_user_error"),
                reply_markup=markups.treasure_bury_back(bot.languages[user.language])
            )
            return
        try:
            amount = int(message.text)
        except ValueError:
            await bot.client.send_message(
                message.chat.id,
                bot.string(user.language, "enter_treasure_amount_not_a_number"),
                reply_markup=markups.treasure_bury_back(bot.languages[user.language])
            )
            return
        if amount > user.sdq_balance:
            await bot.client.send_message(
                message.chat.id,
                bot.string(user.language, "enter_treasure_amount_insufficient_funds", balance=user.sdq_balance),
                reply_markup=markups.treasure_bury_back(bot.languages[user.language])
            )
            return
        treasure_rep = TreasureRepository()
        treasure = Treasure(user.x, user.y, amount, user.id)
        if not treasure_rep.add(treasure):
            await bot.client.send_message(
                message.chat.id,
                bot.string(user.language, "unknown_error"),
                reply_markup=markups.treasure_bury_back(bot.languages[user.language])
            )
            return
        await bot.update_user_balance(user, user_rep, user.sdq_balance-amount)
        await state.finish()
        await bot.send_playground_message(user, message.chat.id, user_rep)