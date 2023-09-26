from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.configurations.inline import cf_key_end_delete_u
from components.keyboards_components.strings.inline import keyb_str_delete_u
from components.texts.admins.manage_users import text_start_delete_users
from components.texts.admins.manage_categories import text_stop_delete_u, text_end_delete_u
from components.tools import get_callb_content, generate_zero_array, get_sure_delete_usr_msg
from components.keyboards_components.generators import get_inline_keyb_markup
from microservices.sql_models_extends.user import UserExtend
from microservices.redis_models.user import RedisUser
from states.admin.steps_manage_categories import StepsDeleteCategories
from states.admin.steps_manage_users import StepsGetListUsers, StepsDeleteUser

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetListUsers.get_list_users, F.data.startswith("delete_users"))
async def start_delete_users(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsDeleteUser.start_delete_users)

    users = await UserExtend.get_admin_users(callback.message.chat.id)

    status_list = await generate_zero_array(len(users))
    list_index_users = []
    list_buttons_name = []

    # Генерируем список порядкового номера пунктов меню в клавиатуре
    for i in range(0, len(users)):
        list_index_users.append(i)

    # Генерируем список наименований кнопок с пунктами меню
    for e in users:
        list_buttons_name.append(f'{e["fullname"].split(" ")[1]} - {e["profession"]}')

    keyboard_users = await get_inline_keyb_markup(
        list_names=list_buttons_name,
        list_data=list_index_users,
        callback_str="delete_choose_users",
        number_cols=2,
    )

    # Сохраняем пользователей и лист статусов пользователей (выбран или нет)
    await state.set_data({
        'list_index_users': list_index_users,
        'status_list': status_list,
        'users': users
    })

    await callback.message.edit_text(text=text_start_delete_users, reply_markup=keyboard_users, parse_mode="html")


@rt.callback_query(StepsDeleteUser.start_delete_users, F.data.startswith("delete_choose_users"))
async def change_delete_users_list(callback: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()

    number_choose_user= int(await get_callb_content(callback.data))
    new_data['status_list'][number_choose_user] = 1 if new_data['status_list'][number_choose_user] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': new_data['status_list'],
    })

    for i in range(0, len(new_data['users'])):
        status_emoji = '' if new_data['status_list'][i] == 0 else '☑️'
        list_names.append(
            f'{status_emoji} {new_data["users"][i]["fullname"].split(" ")[1]} - {new_data["users"][i]["profession"]}')

    keyboard_users = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=new_data['list_index_users'],
        callback_str="delete_choose_users",
        number_cols=2,
        add_keyb_to_start=keyb_str_delete_u
    )

    await callback.message.edit_text(text=text_start_delete_users, reply_markup=keyboard_users, parse_mode="html")


# Предупреждающее сообщение --------------------------------------------------------------------------------------------
@rt.callback_query(StepsDeleteUser.start_delete_users, F.data == "next_step_delete_users")
async def sure_msg_delete_user(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsDeleteCategories.sure_msg_delete_categories)
    state_data = await state.get_data()
    choose_items_names = []

    for i in range(0, len(state_data['users'])):
        if state_data['status_list'][i] == 1:
            choose_items_names.append(state_data['users'][i]['fullname'])

    sure_msg = await get_sure_delete_usr_msg(choose_items_names)

    await callback.message.edit_text(text=sure_msg, reply_markup=cf_key_end_delete_u, parse_mode="html")


@rt.callback_query(StepsDeleteCategories.sure_msg_delete_categories, F.data == "cancel_delete_users")
async def cancel_delete_menu_item(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=text_stop_delete_u, parse_mode="html")


@rt.callback_query(StepsDeleteCategories.sure_msg_delete_categories, F.data == "end_delete_users")
async def end_delete_menu_item(callback: CallbackQuery, state: FSMContext, redis_users: RedisUser):
    state_data = await state.get_data()
    await state.clear()

    choose_users_chat_id_list = []

    for i in range(0, len(state_data['users'])):
        if state_data['status_list'][i] == 1:
            choose_users_chat_id_list.append(state_data['users'][i]['chat_id'])

    # Удаляем их из mysql
    await UserExtend.delete_users_by_chat_ids(choose_users_chat_id_list)

    # Удаляем их из redis
    await redis_users.delete_users(choose_users_chat_id_list)

    await callback.message.edit_text(text=text_end_delete_u, parse_mode="html")