from aiogram.fsm.state import State, StatesGroup


class StepsGetPartnersList(StatesGroup):
    get_list_partners = State()


class StepsAddPartner(StatesGroup):
    start_add_partner = State()


class StepsDeletePartners(StatesGroup):
    start_delete_partners = State()
    sure_msg_delete_partners = State()
