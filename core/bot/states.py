from aiogram.dispatcher.filters.state import State, StatesGroup


class StartingForm(StatesGroup):
    language = State()
    nickname = State()

class TreasureBuryForm(StatesGroup):
    amount = State()