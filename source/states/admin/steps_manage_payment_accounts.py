from aiogram.fsm.state import State, StatesGroup


class StepsGetPaymentAccountsList(StatesGroup):
    get_payment_accounts_list = State()


class StepsAddPaymentAccount(StatesGroup):
    start_add_payment_account = State()
    select_payment_account_organization = State()


class StepsDeletePaymentAccounts(StatesGroup):
    start_delete_payment_accounts = State()
    sure_msg_delete_payment_accounts = State()
