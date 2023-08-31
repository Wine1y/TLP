from aiogram import Bot, Dispatcher, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import Message, InlineKeyboardMarkup, InputMediaPhoto, InputFile
from typing import List, Dict, Any, Optional
from PIL import Image
from datetime import datetime
from random import uniform
from contextlib import suppress

from core.bot.message_handlers import set_message_handlers
from core.bot import markups
from core.bot.callback_handlers import set_callback_handlers
from core.bot.state_handlers import set_state_handlers
from core.bot.language import BotLanguage
from core.map_utils.bot_map import BotMap
from core.map_utils.map_generator import MapGenerator
from core.map_utils.map_renderer import MapRenderer
from core.db import User, UserRepository


class SolarDriveBot():
    client: Bot
    dp: Dispatcher
    map_generator: MapGenerator
    map_renderer: MapRenderer
    map_seed: int
    map_size: int
    energy_coefficient: float
    starting_cords: List[int]
    bot_map: BotMap
    languages: Dict[str, BotLanguage]

    def __init__(
        self,
        token: str,
        map_generator: MapGenerator,
        map_renderer: MapRenderer,
        map_seed: int,
        map_size: int,
        energy_coefficient: float,
        section_size: int,
        starting_cords: List[int],
        languages: Dict[str, BotLanguage]
    ):
        self.client = Bot(token=token)
        self.dp = Dispatcher(self.client, storage=MemoryStorage())
        self.map_generator = map_generator
        self.map_renderer = map_renderer
        self.map_seed = map_seed
        self.map_size = map_size
        self.energy_coefficient = energy_coefficient
        self.section_size = section_size
        self.bot_map = map_generator.BuildMap(map_seed, map_size, map_size)
        self.languages = languages

        self.starting_cords = starting_cords
        if self.starting_cords is None:
            raise RuntimeError("Can't find any walkable tiles on the map")

        set_message_handlers(self)
        set_callback_handlers(self)
        set_state_handlers(self)
    
    def start_polling(self):
        executor.start_polling(self.dp, skip_updates=True)
    
    def string(self, language: str, string_id: str, **values: Any) -> str:
        return self.languages[language].string(string_id, **values)
    
    def user_subsection(self, user: User) -> Image.Image:
        return self.map_renderer.draw_map_subsection(
            self.bot_map,
            [user.x, user.y],
            self.section_size,
            self.section_size
        )
    
    def user_controller_info(self, user: User) -> str:
        return f"X: *{user.x}* Y: *{user.y}*\n{self.string(user.language, 'energy')}: *{round(user.energy)}%*"
    
    async def update_user_balance(self, user: User, rep: UserRepository, new_balance: int) -> bool:
        user.sdq_balance = new_balance
        if not rep.commit():
            return False
        if user.sdq_msg_id is not None:
            await self.client.edit_message_text(
                self.string(user.language, "sdq_msg", balance=new_balance),
                chat_id=user.tg_id,
                message_id=user.sdq_msg_id,
                reply_markup=markups.sqd_msg_markup(self.languages[user.language])
            )
        return True
    
    def refresh_user_energy(self, user: User, rep: UserRepository) -> bool:
        now = round(datetime.utcnow().timestamp())
        if user.last_energy_refresh is not None:
            seconds_passed = now-user.last_energy_refresh
            energy_charged = self.energy_coefficient * seconds_passed * uniform(0.1, 1)
            user.energy = min(round(user.energy+energy_charged, 4), 100)
        user.last_energy_refresh = now
        return rep.commit()

    def update_user_energy(self, user: User, rep: UserRepository, new_energy: int) -> bool:
        user.energy = max(min(new_energy, 100), 0)
        return rep.commit()
    
    async def update_playground_message(
        self,
        message: Message,
        user: User,
        caption: Optional[str]=None,
        markup: Optional[InlineKeyboardMarkup]=None,
        parse_mode:str="Markdown"
    ):
        section_image = self.user_subsection(user)
        with self.map_renderer.get_image_data(section_image) as image_data:
            await message.edit_media(
                InputMediaPhoto(
                    InputFile(image_data, filename=f"{user.x}x{user.y}.png"),
                    caption=caption or self.user_controller_info(user),
                    parse_mode=parse_mode
                ),
                reply_markup=markup or markups.rover_controller()
            )
    
    async def send_playground_message(
        self,
        user: User,
        chat_id: int,
        user_rep: UserRepository
    ):
        background_image = self.map_renderer.get_map_background(self.section_size, self.section_size)
        section_image = self.user_subsection(user)
        self.refresh_user_energy(user, user_rep)
        with self.map_renderer.get_image_data(background_image) as image_data:
            new_msg = await self.client.send_photo(
                caption=self.user_controller_info(user),
                chat_id=chat_id,
                photo=InputFile(image_data, filename=f"{user.x}x{user.y}.png"),
                reply_markup=markups.rover_controller(),
                parse_mode="Markdown"
            )
            if new_msg is None:
                return
        with self.map_renderer.get_image_data(section_image) as image_data:
            await new_msg.edit_media(
                InputMediaPhoto(
                    InputFile(image_data, filename=f"{user.x}x{user.y}.png"),
                    caption=self.user_controller_info(user),
                    parse_mode="Markdown"
                ),
                reply_markup=markups.rover_controller()
            )
            if user.playground_msg_id is not None:
                with suppress(Exception):
                    await self.client.delete_message(chat_id, user.playground_msg_id)
            user.playground_msg_id = new_msg.message_id
            user_rep.commit()