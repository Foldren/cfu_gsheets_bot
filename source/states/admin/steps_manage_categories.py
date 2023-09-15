from aiogram.fsm.state import State, StatesGroup


class StepsGetCategoriesList(StatesGroup):
    get_list_categories = State()


class StepsAddCategory(StatesGroup):
    start_add_category = State()
    choose_observers_category = State()


class StepsDeleteCategories(StatesGroup):
    start_delete_categories = State()
    sure_msg_delete_categories = State()


class StepsChangeCategory(StatesGroup):
    start_change_category = State()
    change_name_category = State()
    change_observers_category = State()




