from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsMemberFilter
from components.keyboards_components.generators import get_keyb_list_notify_types_user, get_notify_keyboard_btn
from components.texts.users.request_money_report import text_get_list_notify_types_user
from components.tools import get_formatted_msg_callb_notifications, get_callb_content, change_stage_report_request
from microservices.sql_models_extends.confirm_notification import ConfirmNotificationExtend
from microservices.sql_models_extends.report_request import ReportRequestExtend
from microservices.sql_models_extends.user import UserExtend
from states.admin.steps_manage_reports_requests import StepsManageRequestReports

rt = Router()

# Ставим на роутер фильтры (приватный чат + категория пользователя)
rt.message.filter(IsMemberFilter(), F.chat.type == "private")
rt.callback_query.filter(IsMemberFilter(), F.message.chat.type == "private")


@rt.message(F.text.endswith("📩"))
async def get_list_notify_categories_user(message: Message, state: FSMContext) -> None:
    await state.clear()

    user_id = message.from_user.id
    user_role = await UserExtend.get_user_role(chat_id=user_id, role_type='report_request')
    user_notifications = await UserExtend.get_notifications(user_id)
    keyboard_markup = await get_keyb_list_notify_types_user(
        user_notifications=user_notifications,
        user_role=user_role,
    )

    await state.set_state(StepsManageRequestReports.get_list_notify_types_user)
    await message.answer(text=text_get_list_notify_types_user, reply_markup=keyboard_markup)


@rt.callback_query(StepsManageRequestReports.get_list_notify_types_user,
                   (F.data.startswith('n_issuance_report') | F.data.startswith('n_conciliate_requests_report') |
                    F.data.startswith('n_approve_requests_report') | F.data.startswith('n_treasure_requests_report')))
async def get_list_notifications_by_category(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик, который выводит список уведомлений по заданной категории

    :param callback: колбек с выбранной категорией уведомлений
    :param state: стейт с выводом списка категорий уведомлений
    """

    await state.clear()
    await state.set_state(StepsManageRequestReports.get_list_notifications_by_category)

    notifications = await UserExtend.get_notifications(chat_id=callback.message.chat.id, type_n=callback.data)
    formatted_msgs = await get_formatted_msg_callb_notifications(notifications=notifications)
    await callback.message.edit_text(text=formatted_msgs['fst_message'])
    for n in formatted_msgs['notifications']:
        keyb_markup = await get_notify_keyboard_btn(n['callback'])
        await callback.message.answer(text=n['text'], reply_markup=keyb_markup)


@rt.callback_query(StepsManageRequestReports.get_list_notifications_by_category,
                   (F.data.startswith('n_report_request') | F.data.startswith('n_issuance_report')))
async def confirm_notification(callback: CallbackQuery) -> None:
    callb_d = await get_callb_content(callback_data=callback.data, multiply_values=True)
    type_notify = callb_d[0]

    if type_notify == 'n_report_request':
        stage_rep_req = callb_d[1]
        id_notify = callb_d[2]
        cfrm_notify = await ConfirmNotificationExtend.get(id_notify)
        rep_req = await cfrm_notify.report_request
        admin_id = await UserExtend.get_user_admin_id(callback.message.chat.id)

        await ConfirmNotificationExtend.delete_by_id(id_notify)

        await change_stage_report_request(
            bot=callback.bot,
            admin_chat_id=admin_id,
            stage=stage_rep_req,
            report_request=rep_req
        )
        await callback.message.delete()






