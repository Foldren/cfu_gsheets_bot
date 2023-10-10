from aiogram import Router, F
from aiogram.exceptions import TelegramBadRequest
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsAdminFilter
from components.keyboards_components.generators import get_inline_keyb_markup, \
    get_keyb_row_save_changes
from components.keyboards_components.keyboards.inline import keyb_start_manage_reports_requests
from components.text_generators.admins import get_text_select_users_by_role, get_alert_by_role
from components.texts.admins.manage_reports_requests import text_start_manage_reports_requests, \
    alert_text_error_load_users_list
from components.tools import get_callb_content, answer_or_edit_message, \
    get_users_keyb_names_with_checkbox, \
    get_changed_reply_keyb_with_checkbox
from microservices.sql_models_extends.user import UserExtend
from states.admin.steps_manage_reports_requests import StepsManageReportsRequests

rt = Router()

# Ставим на роутер фильтры (приватный чат + категория пользователя)
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Алгоритм запроса в подотчет")
async def start_manage_reports_requests(message: Message, state: FSMContext, answer_on_msg: bool = True) -> None:
    """
    Обработчик на reply кнопку 'Алгоритм запроса в подотчет', выводит роли

    :param message: сообщение на любом стейте
    :param state: стейт главного меню
    :param answer_on_msg: флаг для ответа на сообщение (нужно для грамотного возвращения в начало)
    """
    await state.clear()
    await state.set_state(StepsManageReportsRequests.select_role)
    await answer_or_edit_message(
        message=message,
        text=text_start_manage_reports_requests,
        keyboard_markup=keyb_start_manage_reports_requests,
        flag_answer=answer_on_msg
    )


@rt.callback_query(StepsManageReportsRequests.select_role, F.data.startswith("assign"))
async def get_role_users_list(callback: CallbackQuery, state: FSMContext) -> None:
    """
    Обработчик после выбора роли пользователя, выводит пользователей по выбранной роли + без роли

    :param callback: колбек кнопки с ролью (в нем содержится наименование роли)
    :param state: стейт выбора роли
    """
    await state.set_state(StepsManageReportsRequests.select_list_users)
    role = await get_callb_content(callback.data)
    text_msg = await get_text_select_users_by_role(role)
    save_changes_keyb_row = await get_keyb_row_save_changes(f"save_rep_reqs_list:{role}")
    await state.set_data({'role': role, 'text_msg': text_msg})
    s_users = await UserExtend.get_admin_users(
        id_admin=callback.message.chat.id,
        include_admin=True,
        only_none_and_role=role
    )
    names_callb_btns = await get_users_keyb_names_with_checkbox(
        users=s_users,
        flag_name='role_for_reports__role',
        flag_value=role,
        include_admin=True,
        admin_id=callback.message.chat.id
    )
    if not names_callb_btns['names']:
        await callback.answer(alert_text_error_load_users_list)
        try:
            await start_manage_reports_requests(callback.message, state, answer_on_msg=False)
        except TelegramBadRequest:
            pass
        return
    keyboard_markup = await get_inline_keyb_markup(
        list_names=names_callb_btns['names'],
        list_data=names_callb_btns['callbacks'],
        callback_str=f"select_rep_reqs:{role}",
        number_cols=3,
        add_keyb_to_start=save_changes_keyb_row
    )
    await callback.message.edit_text(text=text_msg, reply_markup=keyboard_markup, parse_mode="html")


@rt.callback_query(StepsManageReportsRequests.select_list_users, F.data.startswith("select_rep_reqs"))
async def change_role_users_list(callback: CallbackQuery, state: FSMContext) -> None:
    st_data = await state.get_data()
    new_keyboard_markup = await get_changed_reply_keyb_with_checkbox(callback=callback)
    try:
        await callback.message.edit_text(text=st_data['text_msg'], reply_markup=new_keyboard_markup, parse_mode="html")
    except TelegramBadRequest:
        pass


@rt.callback_query(StepsManageReportsRequests.select_list_users, F.data.startswith("save_rep_reqs_list"))
async def end_manage_reports_requests(callback: CallbackQuery, state: FSMContext) -> None:
    st_data = await state.get_data()
    users_with_new_roles = []
    text_success_alert = await get_alert_by_role(st_data['role'])
    for i, row in enumerate(callback.message.reply_markup.inline_keyboard):
        for k, button in enumerate(row):
            if '☑️' in button.text:
                users_with_new_roles.append(int(button.callback_data.split(":")[2]))
    await UserExtend.change_roles_for_admin_users(
        admin_id=callback.message.chat.id,
        users_chat_id_list=users_with_new_roles,
        role=st_data['role']
    )
    await state.clear()
    # Возвращаемся в начало
    await start_manage_reports_requests(callback.message, state, answer_on_msg=False)
    await callback.answer(text_success_alert)




