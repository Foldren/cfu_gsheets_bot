from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.strings.inline import keyb_str_pass_add_users_to_org
from components.texts.admins.manage_organizations import text_start_add_organization, \
    text_choose_observers_organization, text_end_add_organization
from components.tools import get_callb_content, generate_zero_array, \
    get_msg_list_data
from services.sql_models_extends.organization import OrganizationExtend
from services.sql_models_extends.user import UserExtend
from states.admin.steps_manage_organizations import StepsGetOrganizationsList, StepsAddOrganization
from states.admin.steps_manage_partners import StepsGetPartnersList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.chat.type == "private")


@rt.callback_query(StepsGetPartnersList.get_list_partners, F.data.startswith("add_partner"))
async def start_add_organization(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsAddOrganization.start_add_organization)
    await callback.message.edit_text(text=text_start_add_organization, parse_mode="html")


@rt.message(StepsAddOrganization.start_add_organization)
async def choose_observers_organization(message: Message, state: FSMContext):
    users = await UserExtend.get_admin_users(message.from_user.id)
    status_list = await generate_zero_array(len(users))
    list_msg_data = await get_msg_list_data(message.text)
    list_index_users = []
    list_buttons_name = []

    # Генерируем список порядкового номера пользователей в клавиатуре
    for i in range(0, len(users)):
        list_index_users.append(i)

    # Генерируем список наименований кнопок с пользователями
    for e in users:
        list_buttons_name.append(f'{e["fullname"].split(" ")[1]} - {e["profession"]}')

    keyboard_users = await get_inline_keyb_markup(
        list_names=list_buttons_name,
        list_data=list_index_users,
        callback_str="change_observers_status_list",
        number_cols=2,
        add_keyb_to_start=keyb_str_pass_add_users_to_org
    )

    message_text = f"<b>Параметры нового ЮР Лица</b> ⤵️\n\n" \
                   f"<u>ИНН</u>: <b>{list_msg_data[0]}</b>\n" \
                   f"<u>Название</u>: <b>{list_msg_data[1]}</b>\n" + text_choose_observers_organization

    # Сохраняем название выбранного пункта и лист статусов пользователей (выбран или нет)
    await state.update_data({
        'list_index_users': list_index_users,
        'inn_new_organization': list_msg_data[0],
        'name_new_organization': list_msg_data[1],
        'status_list': status_list,
        'users': users,
        'msg_text': message_text,
    })

    await state.set_state(StepsAddOrganization.choose_observers_organization)
    await message.answer(text=message_text, reply_markup=keyboard_users, parse_mode="html")


# Выбор пользователей для меню -----------------------------------------------------------------------------------------
@rt.callback_query(StepsAddOrganization.choose_observers_organization, F.data.startswith("change_observers_status_list"))
async def change_observers_list(callback: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()
    number_choose_user = int(await get_callb_content(callback.data))
    new_data['status_list'][number_choose_user] = 1 if new_data['status_list'][number_choose_user] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': new_data['status_list'],
    })

    for i in range(0, len(new_data['users'])):
        status_emoji = '' if new_data['status_list'][i] == 0 else '☑️'
        list_names.append(f'{status_emoji} {new_data["users"][i]["fullname"].split(" ")[1]} - {new_data["users"][i]["profession"]}')

    keyboard_users = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=new_data['list_index_users'],
        callback_str="change_observers_status_list",
        number_cols=2,
        add_keyb_to_start=keyb_str_pass_add_users_to_org
    )

    await callback.message.edit_text(
        text=new_data['msg_text'],
        reply_markup=keyboard_users,
        parse_mode="html"
    )


# Сохранение изменений -------------------------------------------------------------------------------------------------
@rt.callback_query(StepsAddOrganization.choose_observers_organization, F.data.startswith("save_new_organization"))
async def save_add_organization(callback: CallbackQuery, state: FSMContext):
    data_organization = await state.get_data()
    list_id_users = []

    # Генерируем список выбранных пользователей
    for i in range(0, len(data_organization['users'])):
        if data_organization['status_list'][i] == 1:
            list_id_users.append(int(data_organization['users'][i]['chat_id']))

    # Добавляем id админа
    list_id_users.append(callback.message.chat.id)

    await OrganizationExtend.add(
        name=data_organization['name_new_organization'],
        inn=data_organization['inn_new_organization'],
        admin_id=callback.from_user.id,
        observers_id_list=list_id_users
    )

    await state.clear()
    await callback.message.edit_text(text=text_end_add_organization, parse_mode="html")


