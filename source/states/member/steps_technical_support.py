from aiogram.fsm.state import State, StatesGroup


class StepsTechnicalSupport(StatesGroup):
    start_write_message_to_support = State()
