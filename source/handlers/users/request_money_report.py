from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsUserFilter
from components.text_generators.users import get_notify_start_request_report
from components.texts.users.request_money_report import text_start_request_money_report, text_send_request_to_agreement, \
    text_no_all_roles_on_request
from components.tools import get_msg_list_data, send_multiply_messages
from microservices.sql_models_extends.notify_group import NotifyGroupExtend
from microservices.sql_models_extends.user import UserExtend
from states.admin.steps_manage_reports_requests import StepsMakeRequestMoneyReport

rt = Router()

# Ставим на роутер фильтры (приватный чат + категория пользователя)
rt.message.filter(IsUserFilter(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Запрос денег в подотчет")
async def start_request_money_report(message: Message, state: FSMContext) -> None:
    """
    Обработчик на начало операции запроса денег в подотчет (первый шаг - ввод суммы и комментария)

    :param message: сообщение из главного меню
    :param state: стейт главного меню
    """
    admin_id = await UserExtend.get_user_admin_id(message.from_user.id)
    roles_exist_flag = await UserExtend.check_all_users_roles_exist(admin_id)

    if roles_exist_flag:
        await state.clear()
        await state.set_state(StepsMakeRequestMoneyReport.start_agreement)
        text_msg = text_start_request_money_report
    else:
        text_msg = text_no_all_roles_on_request
    await message.answer(text=text_msg)


@rt.message(StepsMakeRequestMoneyReport.start_agreement)
async def send_request_to_agreement(message: Message, state: FSMContext) -> None:
    msg_data = await get_msg_list_data(message.text)
    admin_id = await UserExtend.get_user_admin_id(message.chat.id)
    conciliators = await UserExtend.get_users_by_role_and_type(
        id_admin=admin_id,
        role='conciliator',
        role_type='report_request'
    )
    ng_chat_ids = await NotifyGroupExtend.get_admin_notify_groups_chat_ids(admin_id)

    user_nicknames = []
    for c in conciliators:
        user_nicknames.append(c['nickname'])

    msg_text = await get_notify_start_request_report(
        users_nicknames=user_nicknames,
        sender_nickname=message.from_user.username,
        volume=msg_data[0],
        comment=msg_data[1]
    )

    await UserExtend.send_confirm_notify_to_users_by_role(
        admin_id=admin_id,
        role_recipients='conciliator',
        volume=msg_data[0],
        comment=msg_data[1],
        nickname_sender='@' + message.from_user.username,
    )

    await send_multiply_messages(
        bot=message.bot,
        msg_text=msg_text,
        list_chat_ids=ng_chat_ids
    )

    await state.clear()
    await message.answer(text=text_send_request_to_agreement)
