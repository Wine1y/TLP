from typing import Dict, Optional, List
from aiogram.utils.callback_data import CallbackData
from aiogram.types import (InlineKeyboardMarkup, InlineKeyboardButton,
                           ReplyKeyboardMarkup, KeyboardButton)
from aiogram.types import ReplyKeyboardRemove

from core.bot.language import BotLanguage


ROVER_MOVE = CallbackData("move", "direction")
ROVER_DIG = CallbackData("dig", "status")
ROVER_CANCEL = CallbackData("cancel", "new_message")
ROVER_REFRESH = CallbackData("refresh", "count")
ROVER_MOVE_PILE = CallbackData("move_pile", "d_x", "d_y")
CB_WIP = CallbackData("wip")

def remove_keyboard() -> ReplyKeyboardRemove:
    return ReplyKeyboardRemove()

def rover_controller(refresh_count: Optional[int]=None) -> InlineKeyboardMarkup:
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
        InlineKeyboardButton("↻", callback_data=ROVER_REFRESH.new(count=refresh_count or 1))
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
            callback_data=ROVER_CANCEL.new(new_message="False")
        )
    )
    return markup

def treasure_found(language: BotLanguage) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            language.string("take_treasure"),
            callback_data=ROVER_DIG.new(status="treasure_taken")
        ),
        InlineKeyboardButton(
            language.string("leave_treasure"),
            callback_data=ROVER_CANCEL.new(new_message="False")
        )
    )
    return markup

def treasure_not_found(language: BotLanguage) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            language.string("bury_treasure"),
            callback_data=ROVER_DIG.new(status="treasure_bury")
        ),
        InlineKeyboardButton(
            language.string("back"),
            callback_data=ROVER_CANCEL.new(new_message="False")
        )
    )
    return markup

def treasure_bury_back(language: BotLanguage) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            language.string("back"),
            callback_data=ROVER_CANCEL.new(new_message="True")
        )
    )
    return markup

def pile_move_confirm(language: BotLanguage, move_delta: List[int]) -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            language.string("pile_move_confirmed"),
            callback_data=ROVER_MOVE_PILE.new(d_x=move_delta[0], d_y=move_delta[1])
        ),
        InlineKeyboardButton(
            language.string("cancel"),
            callback_data=ROVER_CANCEL.new(new_message="False")
        )
    )
    return markup