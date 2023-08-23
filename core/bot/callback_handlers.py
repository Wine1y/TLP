from aiogram.types import CallbackQuery, InputMediaPhoto, InputFile
from typing import Dict

from core.bot import markups
from core.map_utils.bot_map import MapTile
from core.db import User

_MOVE_DELTAS = {
    "top": (0, -1),
    "bottom": (0, 1),
    "left": (-1, 0),
    "right": (1, 0)
}

def set_callback_handlers(bot: "SolarDriveBot"):
    
    @bot.dp.callback_query_handler(markups.ROVER_MOVE.filter())
    async def move_handler(query: CallbackQuery, callback_data: Dict[str, str]):
        user = User.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        delta = _MOVE_DELTAS[callback_data["direction"]]
        new_cords = bot.bot_map.normalize_cords([user.x+delta[0], user.y+delta[1]])
        if not bot.bot_map.tile_at(new_cords[0], new_cords[1]).walkable:
            await query.answer()
            return
        if User.get_by_coordinates(new_cords[0], new_cords[1]) is not None:
            await query.answer()
            return
        user.x, user.y = new_cords[0], new_cords[1]
        if not user.update():
            await query.answer(bot.string(user.language, "unkown_error"))
            return
        section_image = bot.user_subsection(user)
        with bot.map_renderer.get_image_data(section_image) as image_data:
            await query.message.edit_media(
                InputMediaPhoto(
                    InputFile(image_data, filename=f"{user.x}x{user.y}.png"),
                    caption=bot.user_controller_info(user),
                    parse_mode="Markdown"
                ),
                reply_markup=markups.rover_controller()
            )
    
    @bot.dp.callback_query_handler(markups.ROVER_DIG.filter(status="waiting"))
    async def dig_handler(query: CallbackQuery):
        user = User.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        user_tile = bot.bot_map.tile_at(user.x, user.y)
        if user_tile != MapTile.Sand:
            await query.answer(bot.string(user.language, "dig_not_on_sand"))
            return
        await query.message.edit_caption(
            caption=bot.string(user.language, "confirm_dig"),
            reply_markup=markups.dig_confirm(bot.languages[user.language])
        )
    
    @bot.dp.callback_query_handler(markups.ROVER_DIG.filter(status="canceled"))
    async def dig_canceled(query: CallbackQuery):
        user = User.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        await query.message.edit_caption(
            caption=bot.user_controller_info(user),
            parse_mode="Markdown",
            reply_markup=markups.rover_controller()
        )
        

    @bot.dp.callback_query_handler(markups.CB_WIP.filter())
    async def wip_handler(query: CallbackQuery):
        await query.answer()