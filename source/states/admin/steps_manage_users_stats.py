from aiogram.fsm.state import State, StatesGroup


class StepsManageUsersStats(StatesGroup):
    choose_stats_period = State()
    change_stats_observers = State()
