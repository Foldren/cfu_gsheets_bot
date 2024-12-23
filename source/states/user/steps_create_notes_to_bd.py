from aiogram.fsm.state import State, StatesGroup


class StepsWriteCategoriesToBd(StatesGroup):
    set_sender = State()
    set_organization_name = State()
    set_queue_categories = State()
    set_volume_operation = State()
    choose_bank = State()
    load_check = State()
    pass_load_check = State()


class StepsWriteIssuanceReport(StatesGroup):
    select_organization = State()
    select_worker = State()
    set_volume = State()
    select_payment_method = State()
    select_notify_group = State()


class StepsReturnIssuanceMeans(StatesGroup):
    select_organization = State()
    set_volume = State()
    select_payment_method = State()


class StepsWriteTransfer(StatesGroup):
    select_organization = State()
    set_volume = State()
    select_wallet_sender = State()
    select_wallet_recipient = State()
