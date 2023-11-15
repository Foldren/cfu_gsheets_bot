from aiogram.fsm.state import State, StatesGroup


class StepsAddNewClient(StatesGroup):
    start_add_new_client = State()
