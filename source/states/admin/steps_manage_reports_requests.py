from aiogram.fsm.state import State, StatesGroup


class StepsManageReportsRequests(StatesGroup):
    select_role = State()
    select_list_users = State()


class StepsMakeRequestMoneyReport(StatesGroup):
    start_agreement = State()
    select_list_users = State()

