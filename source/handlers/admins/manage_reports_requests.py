from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery

from components.keyboards_components.keyboards.inline import keyb_start_manage_reports_requests
from components.texts.admins.manage_reports_requests import text_start_manage_reports_requests
from components.texts.admins.manage_user_stats import text_start_manage_stats, text_choose_observers_stats, \
    text_end_change_observers_p_stats
from components.filters import IsAdminFilter, IsAdminModeFilter
from components.keyboards_components.strings.inline import keyb_str_change_observers_ps
from components.tools import get_callb_content, generate_observers_list, answer_or_edit_message
from components.keyboards_components.generators import get_inline_keyb_markup
from config import STATS_UPRAVLYAIKA
from microservices.sql_models_extends.period_stat import PeriodStatExtend
from microservices.sql_models_extends.user import UserExtend
from states.admin.steps_manage_reports_requests import StepsManageReportsRequests
from states.admin.steps_manage_users_stats import StepsManageUsersStats

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Алгоритм запроса в подотчет")
async def start_manage_reports_requests(message: Message, state: FSMContext, answer_or_edit_msg: bool = True):
    await state.clear()
    await state.set_state(StepsManageReportsRequests.select_role_reports_requests)

    await answer_or_edit_message(
        message=message,
        text=text_start_manage_reports_requests,
        keyboard_markup=keyb_start_manage_reports_requests,
        flag_answer=answer_or_edit_msg
    )


@rt.callback_query(StepsManageReportsRequests.select_role_reports_requests, F.data.startswith("assign"))
async def get_role_users_list(callback: CallbackQuery, state: FSMContext):
    role = await get_callb_content(callback.data)

    if role == "conciliators":
        conciliators = await UserExtend.get_admin_users_with_flag_role(
            id_admin=callback.message.chat.id,
            role='conciliator',
            include_admin=True
        )

        buttons_names = []
        buttons_callbacks = []
        for c in conciliators:
            selected_emoji = '☑️' if c['role'] else ''
            if c['chat_id'] == callback.message.chat.id:
                buttons_names.append(f"{selected_emoji} Я")
            else:
                buttons_names.append(f"{selected_emoji} {c['fullname'].split(' ')[1]} - {c['profession']}")
            buttons_callbacks.append(c['chat_id'])

        keyboard_markup = await get_inline_keyb_markup(
            list_names=buttons_names,
            list_data=buttons_callbacks,
            callback_str="conciliator",
            number_cols=3
        )

        await callback.message.edit_text(text="test", reply_markup=keyboard_markup, parse_mode="html")






    # keyboard_markup = callback.message.reply_markup
    #
    # for row in keyboard_markup.inline_keyboard:
    #     for button in row:
    #         print(button.text)
