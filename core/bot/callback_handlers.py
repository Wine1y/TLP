from aiogram.types import CallbackQuery
from aiogram.dispatcher import FSMContext
from typing import Dict

from core.bot import markups, states
from core.map_utils.bot_map import MapTile, put_sand_pile
from core.db import UserRepository, ChangedTileRepository, TreasureRepository


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
        bot.refresh_user_energy(user, rep)
        if round(user.energy) < 1:
            await bot.update_playground_message(
                query.message,
                user,
                caption=bot.string(user.language, "insufficient_energy"),
                markup=markups.insufficient_energy(bot.languages[user.language])
            )
            return
        delta = _MOVE_DELTAS[callback_data["direction"]]
        new_cords = bot.bot_map.normalize_cords([user.x+delta[0], user.y+delta[1]])
        if bot.bot_map.tile_at(new_cords[0], new_cords[1]) == MapTile.SandPile:
            new_pile_cords = bot.bot_map.normalize_cords([new_cords[0]+delta[0], new_cords[1]+delta[1]])
            if not bot.bot_map.can_place_sand_pile(new_pile_cords[0], new_pile_cords[1], rep):
                await query.answer()
                return
            await bot.update_playground_message(
                query.message,
                user,
                caption=bot.string(user.language, "confirm_pile_move"),
                markup=markups.pile_move_confirm(bot.languages[user.language], delta)
            )
        if not bot.bot_map.is_walkable(new_cords[0], new_cords[1], rep):
            await query.answer()
            return
        user.x, user.y = new_cords[0], new_cords[1]
        if not rep.commit():
            await query.answer(bot.string(user.language, "unknown_error"))
            return
        bot.refresh_user_energy(user, rep)
        bot.update_user_energy(user, rep, user.energy-1)
        await bot.update_playground_message(query.message, user)
    
    @bot.dp.callback_query_handler(markups.ROVER_DIG.filter(status="waiting"))
    async def dig_handler(query: CallbackQuery):
        user_rep = UserRepository()
        user = user_rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        if not bot.bot_map.tile_at(user.x, user.y).diggable:
            await query.answer(bot.string(user.language, "dig_not_on_sand"))
            return
        new_sandpile_pos = bot.bot_map.find_new_sandpile_pos([user.x, user.y], user_rep)
        if new_sandpile_pos is None:
            await query.answer(bot.string(user.language, "no_space_to_dig"))
            return
        await query.message.edit_caption(
            caption=bot.string(user.language, "confirm_dig"),
            reply_markup=markups.dig_confirm(bot.languages[user.language])
        )
    
    @bot.dp.callback_query_handler(markups.ROVER_CANCEL.filter(new_message="False"))
    async def dig_canceled(query: CallbackQuery):
        rep = UserRepository()
        user = rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        bot.refresh_user_energy(user, rep)
        await bot.update_playground_message(query.message, user)
    
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
        treasure_rep = TreasureRepository()
        treasure = treasure_rep.get_by_coordinates(user.x, user.y)
        if treasure is not None:
            caption = bot.string(user.language, "treasure_found", sdq_amount=treasure.sdq_amount)
            markup = markups.treasure_found(bot.languages[user.language])
        else:
            caption = bot.string(user.language, "treasure_not_found")
            markup = markups.treasure_not_found(bot.languages[user.language])
        await bot.update_playground_message(query.message, user, caption, markup)
    
    @bot.dp.callback_query_handler(markups.ROVER_DIG.filter(status="treasure_bury"))
    async def treasure_bury(query: CallbackQuery, state: FSMContext):
        rep = UserRepository()
        user = rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        await bot.client.send_message(
            query.message.chat.id,
            bot.string(user.language, "enter_treasure_amount"),
            reply_markup=markups.treasure_bury_back(bot.languages[user.language])
        )
        await query.answer()
        await state.set_state(states.TreasureBuryForm.amount)

    @bot.dp.callback_query_handler(
        markups.ROVER_CANCEL.filter(new_message="True"),
        state=states.TreasureBuryForm
    )
    async def treasure_bury_canceled(query: CallbackQuery, state: FSMContext):
        user_rep = UserRepository()
        user = user_rep.get_by_tg_id(query.from_user.id)
        await state.finish()
        await bot.send_playground_message(user, query.message.chat.id, user_rep)
        await query.answer()
    
    @bot.dp.callback_query_handler(markups.ROVER_CANCEL.filter(new_message="True"))
    async def treasure_bury_canceled_expired(query: CallbackQuery, state: FSMContext):
        await query.answer()
    
    @bot.dp.callback_query_handler(markups.ROVER_DIG.filter(status="treasure_taken"))
    async def take_treasure(query: CallbackQuery):
        user_rep, treasure_rep = UserRepository(), TreasureRepository()
        user = user_rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        treasure = treasure_rep.get_by_coordinates(user.x, user.y)
        if treasure is not None:
            balance_added = await bot.update_user_balance(user, user_rep, user.sdq_balance+treasure.sdq_amount)
            treasure_deleted = treasure_rep.delete(treasure)
            if balance_added and treasure_deleted:
                bot.refresh_user_energy(user, user_rep)
                await bot.update_playground_message(query.message, user)
                return

        await query.answer(bot.string(user.language, "unknown_error"))
        bot.refresh_user_energy(user, user_rep)
        await bot.update_playground_message(query.message, user)
    
    @bot.dp.callback_query_handler(markups.ROVER_MOVE_PILE.filter())
    async def move_pile(query: CallbackQuery, callback_data: Dict[str, str]):
        user_rep, tile_rep = UserRepository(), ChangedTileRepository()
        user = user_rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        bot.refresh_user_energy(user, user_rep)
        if round(user.energy) < 10:
            await bot.update_playground_message(
                query.message,
                user,
                caption=bot.string(user.language, "insufficient_energy"),
                markup=markups.insufficient_energy(bot.languages[user.language])
            )
            return
        delta_x, delta_y = int(callback_data["d_x"]), int(callback_data["d_y"])
        pile_pos = bot.bot_map.normalize_cords([user.x+delta_x, user.y+delta_y])
        new_pile_pos = bot.bot_map.normalize_cords([pile_pos[0]+delta_x, pile_pos[1]+delta_y])

        bot.bot_map.set_changed_tile_at(
            pile_pos[0], pile_pos[1],
            MapTile.GrainySand, tile_rep
        )
        bot.bot_map.set_changed_tile_at(
            new_pile_pos[0], new_pile_pos[1],
            MapTile.SandPile, tile_rep
        )
        bot.update_user_energy(user, user_rep, user.energy-10)
        user.x, user.y = pile_pos[0], pile_pos[1]
        user_rep.commit()
        await bot.update_playground_message(query.message, user)
    
    @bot.dp.callback_query_handler(markups.ROVER_INVITE_FRIENDS.filter())
    async def inivite_ref_handler(query: CallbackQuery):
        user_rep = UserRepository()
        user = user_rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        await bot.update_playground_message(
            query.message,
            user,
            caption=bot.string(user.language, "ref_invitation_text"),
            markup=markups.invitation_back(bot.languages[user.language]),
            parse_mode=None
        )

    @bot.dp.callback_query_handler(markups.ROVER_REFRESH.filter())
    async def refresh_handler(query: CallbackQuery, callback_data: Dict[str, str]):
        user_rep = UserRepository()
        user = user_rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        markup = markups.rover_controller(refresh_count=int(callback_data["count"])+1)
        bot.refresh_user_energy(user, user_rep)
        await bot.update_playground_message(query.message, user, markup=markup)
    
    @bot.dp.callback_query_handler(markups.ROVER_START.filter())
    async def start_handler(query: CallbackQuery):
        user_rep = UserRepository()
        user = user_rep.get_by_tg_id(query.from_user.id)
        if user is None:
            await query.answer(bot.string("English", "no_user_error"))
            return
        await query.answer()
        await bot.send_playground_message(user, query.message.chat.id, user_rep)
        
    @bot.dp.callback_query_handler(markups.CB_WIP.filter())
    async def wip_handler(query: CallbackQuery):
        await query.answer()