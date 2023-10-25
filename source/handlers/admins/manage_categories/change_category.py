from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.inline_strings import keyb_str_change_observers_mi
from components.texts.admins.manage_categories import text_choose_param_to_change_menu_item, \
    text_start_change_menu_item, text_change_name_menu_item, text_end_change_name_menu_item, \
    text_start_change_observers_menu_item, text_end_change_observers_menu_item
from components.tools import get_callb_content, get_msg_queue, generate_observers_list, get_str_format_queue
from components.keyboards_components.generators import get_inline_keyb_markup, get_inline_keyb_change_menu_item
from microservices.sql_models_extends.category import CategoryExtend
from states.admin.steps_manage_categories import StepsChangeCategory, StepsGetCategoriesList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetCategoriesList.get_list_categories,
                   F.data.startswith("change_menu_items") | (F.data == 'change_upper_menu_items'))
async def start_change_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsChangeCategory.start_change_category)

    parent_category_id = await get_callb_content(callback.data) if "change_upper_menu_items" not in callback.data else None
    categories = await CategoryExtend.get_user_categories_by_parent_id(callback.message.chat.id, parent_category_id)
    parent_category = await CategoryExtend.get_by_id(parent_category_id)
    queue = await get_str_format_queue(parent_category_id) if parent_category_id is not None else ""

    keyboard = await get_inline_keyb_markup(
        list_names=[(e["name"] + ("  💤" if e["status"] == 0 else "")) for e in categories],
        list_data=[e["id"] for e in categories],
        callback_str="change_menu_item",
        number_cols=2,
    )

    text_queue = await get_msg_queue(
        level=parent_category.level if parent_category_id is not None else 0,
        selected_item_name=parent_category.name if parent_category_id is not None else "",
        queue=queue
    )

    await callback.message.edit_text(
        text=f"<b>Редактирование категории:</b> (шаг 1)\n\n" + text_queue + text_start_change_menu_item,
        reply_markup=keyboard,
        parse_mode="html"
    )


@rt.callback_query(StepsChangeCategory.start_change_category,
                   F.data.startswith("change_menu_item") | F.data.startswith("change_status_menu_item"))
async def choose_category_params_to_change(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsChangeCategory.start_change_category)

    id_category = await get_callb_content(callback.data)
    category = await CategoryExtend.get_by_id(id_category)
    level_category = category.level if id_category is not None else 0
    queue = await get_str_format_queue(id_category) if id_category is not None else ""

    if "change_status_menu_item" in callback.data:
        await CategoryExtend.invert_status(category)

    text_queue = await get_msg_queue(
        level=level_category,
        selected_item_name=category.name if id_category is not None else "",
        queue=queue,
        only_queue=True,
    )

    text_name_c = f"<u>Выбрана категория</u>: <b>{category.name}</b>\n"
    text_queue = text_queue if level_category != 1 else ""

    await state.set_data({
        'queue_text': text_name_c + text_queue,
        'id_menu_item': id_category,
    })

    final_text = f"<b>Редактирование категории:</b> (шаг 2)\n\n" + text_name_c + text_queue \
                 + text_choose_param_to_change_menu_item

    keyboard = await get_inline_keyb_change_menu_item(
        id_menu_item=category.id,
        status_menu_item=category.status
    )

    await callback.message.edit_text(text=final_text, reply_markup=keyboard, parse_mode="html")


# Изменение названия ---------------------------------------------------------------------------------------------------
@rt.callback_query(StepsChangeCategory.start_change_category, F.data.startswith("change_name_menu_item"))
async def start_change_name_category(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsChangeCategory.change_name_category)
    state_data = await state.get_data()
    await callback.message.edit_text(
        text=f"<b>Редактирование категории:</b> (шаг 3)\n\n" + state_data['queue_text'] + text_change_name_menu_item,
        parse_mode="html"
    )


@rt.message(StepsChangeCategory.change_name_category)
async def end_change_name_category(message: Message, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()
    await CategoryExtend.update_by_id(category_id=state_data['id_menu_item'], name=message.text)
    await message.answer(text=text_end_change_name_menu_item, parse_mode="html")


# Изменение списка наблюдателей ----------------------------------------------------------------------------------------
@rt.callback_query(StepsChangeCategory.start_change_category, F.data.startswith("start_change_observers_menu_item"))
async def start_change_observers_category(callback: CallbackQuery, state: FSMContext):
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
        text=f"<b>Редактирование категории:</b> (шаг 3)\n\n" + data_state['queue_text'] + text_start_change_observers_menu_item,
        reply_markup=keyboard_users,
        parse_mode="html"
    )


@rt.callback_query(StepsChangeCategory.change_observers_category, F.data.startswith("change_observers_menu_item"))
async def change_observers_category(callback: CallbackQuery, state: FSMContext):
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
async def end_change_observers_category(callback: CallbackQuery, state: FSMContext):
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
