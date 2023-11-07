from aiogram.fsm.state import State, StatesGroup


class StepsShowUserStats(StatesGroup):
    show_main_stats = State()
