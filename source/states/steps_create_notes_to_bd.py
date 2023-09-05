from aiogram.fsm.state import State, StatesGroup


class BrowseMenuItems(StatesGroup):
    get_list_menu_items = State()


class WriteMenuItemsToBd(StatesGroup):
    set_volume_operation = State()
    choose_bank = State()
    load_check = State()
