from io import BytesIO
from aiogram.types import CallbackQuery, InputMediaPhoto, InputFile
from typing import Dict

from core.bot.markups import ROVER_MOVE, CB_WIP, get_rover_controller
from core.db import User

_MOVE_DELTAS = {
    "top": (0, -1),
    "bottom": (0, 1),
    "left": (-1, 0),
    "right": (1, 0)
}

def set_callback_handlers(bot: "SolarDriveBot"):
    
    @bot.dp.callback_query_handler(ROVER_MOVE.filter())
    async def move_handler(query: CallbackQuery, callback_data: Dict[str, str]):
        user = User.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer("К сожалению, произошла ошибка.")
            return
        delta = _MOVE_DELTAS[callback_data["direction"]]
        new_cords = bot.bot_map.normalize_cords([user.x+delta[0], user.y+delta[1]])
        if not bot.bot_map.tile_at(new_cords[0], new_cords[1]).value.walkable:
            await query.answer()
            return
        user.x, user.y = new_cords[0], new_cords[1]
        if not user.update():
            await query.answer("К сожалению, произошла ошибка.")
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
            await query.message.edit_media(
                InputMediaPhoto(
                	InputFile(buffer, filename=f"{user.x}x{user.y}.png"),
                	caption=f"X: *{user.x}* Y: *{user.y}*\nЭнергия: *{user.energy}%*",
                	parse_mode="Markdown"
                ),
                reply_markup=get_rover_controller()
            )
    @bot.dp.callback_query_handler(CB_WIP.filter())
    async def wip_handler(query: CallbackQuery):
    	await query.answer()