from aiogram.fsm.state import State, StatesGroup


class StepsGetBanksList(StatesGroup):
    get_list_banks = State()


class StepsAddBank(StatesGroup):
    start_add_bank = State()
    select_bank_name = State()


class StepsDeleteBanks(StatesGroup):
    start_delete_banks = State()
    sure_msg_delete_banks = State()
