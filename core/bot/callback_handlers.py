from aiogram.types import CallbackQuery, InputMediaPhoto, InputFile
from typing import Dict

from core.bot import markups
from core.map_utils.bot_map import MapTile, put_sand_pile
from core.db import UserRepository, ChangedTileRepository

_MOVE_DELTAS = {
    "top": (0, -1),
    "bottom": (0, 1),
    "left": (-1, 0),
    "right": (1, 0)
}

def set_callback_handlers(bot: "SolarDriveBot"):
    
    @bot.dp.callback_query_handler(markups.ROVER_MOVE.filter())
    async def move_handler(query: CallbackQuery, callback_data: Dict[str, str]):
        rep = UserRepository()
        user = rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        delta = _MOVE_DELTAS[callback_data["direction"]]
        new_cords = bot.bot_map.normalize_cords([user.x+delta[0], user.y+delta[1]])
        if not bot.bot_map.tile_at(new_cords[0], new_cords[1]).walkable:
            await query.answer()
            return
        if rep.get_by_coordinates(new_cords[0], new_cords[1]) is not None:
            await query.answer()
            return
        user.x, user.y = new_cords[0], new_cords[1]
        if not rep.commit():
            await query.answer(bot.string(user.language, "unknown_error"))
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
        rep = UserRepository()
        user = rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        if bot.bot_map.tile_at(user.x, user.y) != MapTile.Sand:
            await query.answer(bot.string(user.language, "dig_not_on_sand"))
            return
        new_sandpile_pos = bot.bot_map.find_new_sandpile_pos([user.x, user.y], rep)
        if new_sandpile_pos is None:
            await query.answer(bot.string(user.language, "no_space_to_dig"))
            return
        await query.message.edit_caption(
            caption=bot.string(user.language, "confirm_dig"),
            reply_markup=markups.dig_confirm(bot.languages[user.language])
        )
    
    @bot.dp.callback_query_handler(markups.ROVER_DIG.filter(status="canceled"))
    async def dig_canceled(query: CallbackQuery):
        rep = UserRepository()
        user = rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        await query.message.edit_caption(
            caption=bot.user_controller_info(user),
            parse_mode="Markdown",
            reply_markup=markups.rover_controller()
        )
    
    @bot.dp.callback_query_handler(markups.ROVER_DIG.filter(status="confirmed"))
    async def dig_confirmed(query: CallbackQuery):
        user_rep, tiles_rep = UserRepository(), ChangedTileRepository()
        user = user_rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        if user.sdq_balance < 1:
            await query.answer(bot.string(user.language, "insufficient_funds", balance=user.sdq_balance))
            return
        new_sandpile_pos = bot.bot_map.find_new_sandpile_pos([user.x, user.y], user_rep)
        if new_sandpile_pos is None:
            await query.answer(bot.string(user.language, "no_space_to_dig"))
            return
        digged =bot.bot_map.set_changed_tile_at(user.x, user.y, MapTile.GrainySand, tiles_rep)
        piled = bot.bot_map.set_changed_tile_at(
            new_sandpile_pos[0],
            new_sandpile_pos[1],
            put_sand_pile(bot.bot_map.tile_at(new_sandpile_pos[0], new_sandpile_pos[1])),
            tiles_rep
        )
        if not digged or not piled:
            await query.answer(bot.string(user.language, "unknown_error"))
            return
        await bot.update_user_balance(user, user_rep, user.sdq_balance-1)
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
        

    @bot.dp.callback_query_handler(markups.CB_WIP.filter())
    async def wip_handler(query: CallbackQuery):
        await query.answer()