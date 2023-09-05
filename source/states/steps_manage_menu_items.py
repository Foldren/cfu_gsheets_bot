from aiogram.fsm.state import State, StatesGroup


class StepsGetListMenu(StatesGroup):
    get_list_menu_items = State()


class StepsAddMenuItem(StatesGroup):
    start_add_menu_item = State()
    choose_observers_menu_item = State()


class StepsDeleteMenuItem(StatesGroup):
    start_delete_menu_item = State()
    sure_msg_delete_item = State()


class StepsChangeMenuItem(StatesGroup):
    start_change_menu_item = State()
    change_name_menu_item = State()
    change_observers_menu_item = State()




