from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter
from components.keyboards_components.generators import get_keyb_list_notify_types_user
from components.texts.users.request_money_report import text_get_list_notify_types_user
from microservices.sql_models_extends.user import UserExtend
from states.admin.steps_manage_reports_requests import StepsManageRequestReports

rt = Router()

# Ставим на роутер фильтры (приватный чат + категория пользователя)
rt.message.filter(IsUserFilter(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


@rt.message(F.text.endswith("📩"))
async def get_list_notify_categories_user(message: Message, state: FSMContext) -> None:
    await state.clear()

    user_id = message.from_user.id
    user_role = await UserExtend.get_user_role(user_id)
    user_notifications = await UserExtend.get_notifications(user_id)
    keyboard_markup = await get_keyb_list_notify_types_user(
        user_chat_id=user_id,
        user_notifications=user_notifications,
        user_role=user_role,
    )

    await state.set_state(StepsManageRequestReports.get_list_notify_types_user)
    await message.answer(text=text_get_list_notify_types_user, reply_markup=keyboard_markup)


@rt.callback_query(StepsManageRequestReports.get_list_notify_types_user,
                   (F.data.startswith('open_notifies_issuance_of_report') |
                    F.data.startswith('open_notifies_conciliate_requests_report') |
                    F.data.startswith('open_notifies_approve_requests_report') |
                    F.data.startswith('open_notifies_treasure_requests_report')))
async def get_list_notifications_by_category(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик, который выводит список уведомлений по заданной категории

    :param callback: колбек с выбранной категорией уведомлений
    :param state: стейт с выводом списка категорий уведомлений
    """

    await state.clear()
    await state.set_state(StepsManageRequestReports.get_list_notifications_by_category)



