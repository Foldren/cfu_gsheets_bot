from aiogram.fsm.state import State, StatesGroup


class StepsGetListUsers(StatesGroup):
    get_list_users = State()


class StepsAddUser(StatesGroup):
    start_add_user = State()
    get_user_id = State()


class StepsChangeUser(StatesGroup):
    start_change_user = State()
    choose_new_data_user = State()
    set_new_main_data_user = State()
    set_new_id_user = State()


class StepsDeleteUser(StatesGroup):
    start_delete_users = State()






