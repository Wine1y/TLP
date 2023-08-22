from aiogram.utils.callback_data import CallbackData
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

ROVER_MOVE = CallbackData("move", "direction")
CB_WIP = CallbackData("wip")

def get_rover_controller() -> InlineKeyboardMarkup:
    markup = InlineKeyboardMarkup(row_width=3)
    markup.add(
        InlineKeyboardButton(" ", callback_data=CB_WIP.new()),
        InlineKeyboardButton("⬆️", callback_data=ROVER_MOVE.new(direction="top")),
        InlineKeyboardButton(" ", callback_data=CB_WIP.new()),
        InlineKeyboardButton("⬅️", callback_data=ROVER_MOVE.new(direction="left")),
        InlineKeyboardButton(" ", callback_data=CB_WIP.new()),
        InlineKeyboardButton("➡️", callback_data=ROVER_MOVE.new(direction="right")),
        InlineKeyboardButton(" ", callback_data=CB_WIP.new()),
        InlineKeyboardButton("⬇️", callback_data=ROVER_MOVE.new(direction="bottom")),
        InlineKeyboardButton(" ", callback_data=CB_WIP.new())
    )
    return markup