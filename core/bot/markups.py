from typing import Dict
from aiogram.utils.callback_data import CallbackData
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton)
from aiogram.types import ReplyKeyboardRemove

from core.bot.language import BotLanguage


ROVER_MOVE = CallbackData("move", "direction")
ROVER_DIG = CallbackData("dig", "status")
CB_WIP = CallbackData("wip")

def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()

def rover_controller() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton(" ", callback_data=CB_WIP.new()),
        InlineKeyboardButton("⬆️", callback_data=ROVER_MOVE.new(direction="top")),
        InlineKeyboardButton(" ", callback_data=CB_WIP.new()),
        InlineKeyboardButton("⬅️", callback_data=ROVER_MOVE.new(direction="left")),
        InlineKeyboardButton("⛏️", callback_data=ROVER_DIG.new(status="waiting")),
        InlineKeyboardButton("➡️", callback_data=ROVER_MOVE.new(direction="right")),
        InlineKeyboardButton(" ", callback_data=CB_WIP.new()),
        InlineKeyboardButton("⬇️", callback_data=ROVER_MOVE.new(direction="bottom")),
        InlineKeyboardButton(" ", callback_data=CB_WIP.new())
    )
    return markup

def languages_markup(languages: Dict[str, BotLanguage]) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, row_width=3, one_time_keyboard=True)
    markup.add(
        *[
            KeyboardButton(language_name)
            for language_name in languages
        ]
    )
    return markup

def nickname_markup(nickname: str) -> ReplyKeyboardMarkup:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    markup.add(
        KeyboardButton(nickname)
    )
    return markup

def sqd_msg_markup(language: BotLanguage) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            language.string("sdq_button_text"),
            callback_data=CB_WIP.new()
        )
    )
    return markup

def dig_confirm(language: BotLanguage) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            language.string("dig_confirmed"),
            callback_data=ROVER_DIG.new(status="confirmed")
        ),
        InlineKeyboardButton(
            language.string("cancel"),
            callback_data=ROVER_DIG.new(status="canceled")
        )
    )
    return markup