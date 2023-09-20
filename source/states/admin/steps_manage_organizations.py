from aiogram.fsm.state import State, StatesGroup


class StepsGetOrganizationsList(StatesGroup):
    get_list_organizations = State()


class StepsAddOrganization(StatesGroup):
    start_add_organization = State()
    choose_observers_organization = State()


class StepsDeleteOrganizations(StatesGroup):
    start_delete_organizations = State()
    sure_msg_delete_organizations = State()


class StepsChangeOrganization(StatesGroup):
    start_change_organization = State()
    change_params_organization = State()
    change_observers_organization = State()




