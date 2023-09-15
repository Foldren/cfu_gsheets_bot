from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.strings.inline import keyb_str_change_observers_mi
from components.texts.admins.manage_categories import text_choose_param_to_change_menu_item, \
    text_start_change_menu_item, text_change_name_menu_item, text_end_change_name_menu_item, \
    text_start_change_observers_menu_item, text_end_change_observers_menu_item
from components.tools import get_callb_content, get_msg_queue, generate_observers_list, get_str_format_queue
from components.keyboards_components.generators import get_inline_keyb_markup, get_inline_keyb_change_menu_item
from services.sql_models_extends.category import CategoryExtend
from states.admin.steps_manage_categories import StepsChangeCategory, StepsGetCategoriesList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage())
rt.callback_query.filter(IsAdminFilter())


@rt.callback_query(StepsGetCategoriesList.get_list_categories,
                   F.data.startswith("change_menu_items") | (F.data == 'change_upper_menu_items'))
async def start_change_menu_item(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsChangeCategory.start_change_category)

    parent_item_id = await get_callb_content(callback.data) if "change_upper_menu_items" not in callback.data else None
    menu_items = await CategoryExtend.get_user_categories_by_parent_id(callback.message.chat.id, parent_item_id)
    parent_item = await CategoryExtend.get_by_id(parent_item_id)
    queue = await get_str_format_queue(parent_item_id) if parent_item_id is not None else ""

    keyboard = await get_inline_keyb_markup(
        list_names=[(e["name"] + ("  💤" if e["status"] == 0 else "")) for e in menu_items],
        list_data=[e["id"] for e in menu_items],
        callback_str="change_menu_item",
        number_cols=2,
    )

    text_queue = await get_msg_queue(
        level=parent_item.level if parent_item_id is not None else 0,
        selected_item_name=parent_item.name if parent_item_id is not None else "",
        queue=queue
    )

    await callback.message.edit_text(text=text_queue + text_start_change_menu_item, reply_markup=keyboard,
                                     parse_mode="html")


@rt.callback_query(StepsChangeCategory.start_change_category,
                   F.data.startswith("change_menu_item") | F.data.startswith("change_status_menu_item"))
async def choose_menu_item_params_to_change(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsChangeCategory.start_change_category)

    id_menu_item = await get_callb_content(callback.data)
    menu = await CategoryExtend.get_by_id(id_menu_item)
    level_menu = menu.level if id_menu_item is not None else 0
    queue = await get_str_format_queue(id_menu_item) if id_menu_item is not None else ""

    if "change_status_menu_item" in callback.data:
        await CategoryExtend.invert_status(menu)

    text_queue = await get_msg_queue(
        level=level_menu,
        selected_item_name=menu.name if id_menu_item is not None else "",
        queue=queue,
        only_queue=True,
    )

    text_name_c = f"<u>Выбран пункт</u>: <b>{menu.name}</b>\n" if level_menu != 1 else f"<u>Выбрано юр. лицо</u>: " \
                                                                                       f"<b>{menu.name}</b>\n"

    text_queue = text_queue if level_menu != 1 else ""

    await state.set_data({
        'queue_text': text_name_c + text_queue,
        'id_menu_item': id_menu_item,
    })

    final_text = text_name_c + text_queue + text_choose_param_to_change_menu_item

    keyboard = await get_inline_keyb_change_menu_item(
        id_menu_item=menu.id,
        status_menu_item=menu.status
    )

    await callback.message.edit_text(text=final_text, reply_markup=keyboard, parse_mode="html")


# Изменение названия ---------------------------------------------------------------------------------------------------
@rt.callback_query(StepsChangeCategory.start_change_category, F.data.startswith("change_name_menu_item"))
async def start_change_name_menu_item(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsChangeCategory.change_name_category)

    state_data = await state.get_data()

    await callback.message.edit_text(text=state_data['queue_text'] + text_change_name_menu_item, parse_mode="html")


@rt.message(StepsChangeCategory.change_name_category)
async def end_change_name_menu_item(message: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()

    await CategoryExtend.update_by_id(category_id=state_data['id_menu_item'], name=message.text)

    await message.answer(text=text_end_change_name_menu_item, parse_mode="html")


# Изменение списка наблюдателей ----------------------------------------------------------------------------------------
@rt.callback_query(StepsChangeCategory.start_change_category, F.data.startswith("start_change_observers_menu_item"))
async def start_change_observers_menu_item(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsChangeCategory.change_observers_category)

    data_state = await state.get_data()
    item_id = await get_callb_content(callback.data)
    users_and_obs = await CategoryExtend.get_admin_users_with_flag_observer(admin_id=callback.message.chat.id,
                                                                            category_id=item_id)
    status_list = await generate_observers_list(users_and_obs)
    list_index_users = []
    list_buttons_name = []

    # Генерируем список порядкового номера пользователей в клавиатуре
    for i in range(0, len(users_and_obs)):
        list_index_users.append(i)

    # Генерируем список наименований кнопок с пользователями
    for e in users_and_obs:
        status_emoji = "☑️" if e["observer"] else ""
        list_buttons_name.append(f'{status_emoji} {e["fullname"].split(" ")[1]} - {e["profession"]}')

    keyboard_users = await get_inline_keyb_markup(
        list_names=list_buttons_name,
        list_data=list_index_users,
        callback_str="change_observers_menu_item",
        number_cols=2,
        add_keyb_to_start=keyb_str_change_observers_mi
    )

    # Сохраняем название выбранного пункта и лист статусов пользователей (выбран или нет)
    await state.update_data({
        'list_index_users': list_index_users,
        'status_list': status_list,
        'users_and_obs': users_and_obs,
    })

    await callback.message.edit_text(
        text=data_state['queue_text'] + text_start_change_observers_menu_item,
        reply_markup=keyboard_users,
        parse_mode="html"
    )


@rt.callback_query(StepsChangeCategory.change_observers_category, F.data.startswith("change_observers_menu_item"))
async def change_observers_menu_item(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsChangeCategory.change_observers_category)

    data_state = await state.get_data()
    number_choose_user = int(await get_callb_content(callback.data))
    data_state['status_list'][number_choose_user] = 1 if data_state['status_list'][number_choose_user] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': data_state['status_list'],
    })

    for i in range(0, len(data_state['users_and_obs'])):
        status_emoji = '' if data_state['status_list'][i] == 0 else '☑️'
        list_names.append(
            f'{status_emoji} {data_state["users_and_obs"][i]["fullname"].split(" ")[1]} - {data_state["users_and_obs"][i]["profession"]}')

    keyboard_users = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=data_state['list_index_users'],
        callback_str="change_observers_menu_item",
        number_cols=2,
        add_keyb_to_start=keyb_str_change_observers_mi
    )

    await callback.message.edit_text(
        text=data_state['queue_text'] + text_start_change_observers_menu_item,
        reply_markup=keyboard_users,
        parse_mode="html"
    )


@rt.callback_query(StepsChangeCategory.change_observers_category, F.data == "save_change_obs_menu_item")
async def end_change_observers_menu_item(callback: CallbackQuery, state: FSMContext):
    data_state = await state.get_data()
    await state.clear()

    list_id_users = []

    # Генерируем список выбранных пользователей
    for i in range(0, len(data_state['users_and_obs'])):
        if data_state['status_list'][i] == 1:
            list_id_users.append(int(data_state['users_and_obs'][i]['chat_id']))

    # Добавляем id админа
    list_id_users.append(callback.message.chat.id)

    await CategoryExtend.update_by_id(category_id=data_state['id_menu_item'], observers_id_list=list_id_users)

    await callback.message.edit_text(
        text=text_end_change_observers_menu_item,
        parse_mode="html"
    )
