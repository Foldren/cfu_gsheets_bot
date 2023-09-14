from aiogram.fsm.state import State, StatesGroup


class StepsChangeWalletList(StatesGroup):
    change_wallets_list = State()
