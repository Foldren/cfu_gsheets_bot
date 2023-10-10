from aiogram.fsm.state import State, StatesGroup


class StepsManageReportsRequests(StatesGroup):
    select_role = State()
    select_list_users = State()


