from aiogram.fsm.state import State, StatesGroup


class BrowseMenuItems(StatesGroup):
    get_list_menu_items = State()


class WriteMenuItemsToBd(StatesGroup):
    set_volume_operation = State()
    choose_bank = State()
    load_check = State()


class WriteIssuanceReport(StatesGroup):
    select_ip = State()
    select_worker = State()
    set_volume = State()
    select_payment_method = State()
    select_notify_group = State()


class ReturnIssuanceMeans(StatesGroup):
    select_ip = State()
    set_volume = State()
    select_payment_method = State()
