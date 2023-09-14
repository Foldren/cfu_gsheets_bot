from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards import keyb_str_pass_add_users_to_mi
from components.admins.texts import text_start_add_menu_item, text_choose_observers_menu_item, text_end_add_menu_item
from components.tools import get_callb_content, get_inline_keyb_markup, get_msg_queue, generate_zero_array, \
    get_str_format_queue
from services.models_extends.menu_item import MenuItemApi
from services.models_extends.user import UserApi
from states.admin.steps_manage_menu_items import StepsGetListMenu, StepsAddMenuItem

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage())
rt.callback_query.filter(IsAdminFilter())


# Сообщение с просьбой указать название нового пункта меню (категории)
@rt.callback_query(StepsGetListMenu.get_list_menu_items, F.data.startswith("add_menu_item") | (F.data == 'add_upper_menu_item'))
async def start_add_menu_item(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsAddMenuItem.start_add_menu_item)

    id_parent_menu = await get_callb_content(callback.data) if "add_menu_item" in callback.data else None
    menu = await MenuItemApi.get_by_id(id_parent_menu) if id_parent_menu is not None else None
    queue = await get_str_format_queue(id_parent_menu) if id_parent_menu is not None else ""

    text_lvl = await get_msg_queue(
        level=menu.level if id_parent_menu is not None else 0,
        selected_item_name=menu.name if id_parent_menu is not None else "",
        queue=queue,
        only_queue=True,
    )

    # Сохраняем id родительского меню и уровень в стейт
    await state.set_data({
        'id_parent_menu': id_parent_menu,
        'text_level': text_lvl,
        'level_new_menu': (menu.level + 1) if menu is not None else 1
    })

    await callback.message.edit_text(text=text_lvl + text_start_add_menu_item, parse_mode="html")


@rt.message(StepsAddMenuItem.start_add_menu_item)
async def choose_observers_menu_item(message: Message, state: FSMContext):
    md = await state.get_data()
    users = await UserApi.get_admin_users(message.from_user.id)
    status_list = await generate_zero_array(len(users))
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
        add_keyb_to_start=keyb_str_pass_add_users_to_mi
    )

    message_text = f"<u>Название новой категории</u>: <b>{message.text}</b>\n" + text_choose_observers_menu_item

    # Сохраняем название выбранного пункта и лист статусов пользователей (выбран или нет)
    await state.update_data({
        'list_index_users': list_index_users,
        'name_new_item': message.text,
        'status_list': status_list,
        'users': users,
        'text_level': md['text_level'] + f"<u>Название новой категории</u>: <b>{message.text}</b>\n",
    })

    await state.set_state(StepsAddMenuItem.choose_observers_menu_item)
    await message.answer(text=md['text_level'] + message_text, reply_markup=keyboard_users, parse_mode="html")


# Выбор пользователей для меню -----------------------------------------------------------------------------------------
@rt.callback_query(StepsAddMenuItem.choose_observers_menu_item, F.data.startswith("change_observers_status_list"))
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
        add_keyb_to_start=keyb_str_pass_add_users_to_mi
    )

    await callback.message.edit_text(
        text=new_data['text_level'] + text_choose_observers_menu_item,
        reply_markup=keyboard_users,
        parse_mode="html"
    )


# Сохранение изменений -------------------------------------------------------------------------------------------------
@rt.callback_query(StepsAddMenuItem.choose_observers_menu_item, F.data.startswith("save_new_menu_item"))
async def save_add_menu_item(callback: CallbackQuery, state: FSMContext):
    data_menu_item = await state.get_data()
    list_id_users = []

    # Генерируем список выбранных пользователей
    for i in range(0, len(data_menu_item['users'])):
        if data_menu_item['status_list'][i] == 1:
            list_id_users.append(int(data_menu_item['users'][i]['chat_id']))

    # Добавляем id админа
    list_id_users.append(callback.message.chat.id)

    await MenuItemApi.add(
        name_item=data_menu_item['name_new_item'],
        lvl_item=data_menu_item['level_new_menu'],
        parent_menu_item_id=data_menu_item['id_parent_menu'],
        observers_id_list=list_id_users
    )

    await state.clear()
    await callback.message.edit_text(text=text_end_add_menu_item, parse_mode="html")


