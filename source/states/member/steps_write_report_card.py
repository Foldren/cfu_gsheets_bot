from aiogram.fsm.state import State, StatesGroup


class StepsWriteReportCard(StatesGroup):
    change_user_type_report_card = State()
