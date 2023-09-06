from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsAdminFilter
from components.keyboards import keyb_str_delete_mi, cf_key_end_delete_mi
from components.texts import text_start_delete_menu_item, \
    text_stop_delete_menu_item, text_end_delete_menu_item
from components.tools import get_callb_content, get_msg_queue, get_inline_keyb_markup, \
    generate_zero_array, get_sure_delete_mi_msg
from services.database_extends.menu_item import MenuItemApi
from states.steps_manage_menu_items import StepsGetListMenu, StepsDeleteMenuItem

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


@rt.callback_query(StepsGetListMenu.get_list_menu_items,
                   F.data.startswith("delete_menu_items") | (F.data == 'delete_upper_menu_items'))
async def start_delete_menu_item(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsDeleteMenuItem.start_delete_menu_item)

    # Проверка на верхнее меню
    if "delete_menu_items" in callback.data:
        parent_item_id = await get_callb_content(callback.data)
        parent_item = await MenuItemApi.get_by_id(parent_item_id)
        level_item = parent_item.level
        name_item = parent_item.name
        queue_item = parent_item.queue
    else:
        parent_item_id = None
        level_item = 0
        name_item = "Юр. Лица"
        queue_item = ""

    msg_queue = await get_msg_queue(level=level_item, selected_item_name=name_item, queue=queue_item)

    menu_items = await MenuItemApi.get_user_items_by_parent_id(
        user_id=callback.message.chat.id,
        parent_id=parent_item_id
    )

    status_list = await generate_zero_array(len(menu_items))
    list_index_menu_items = []
    list_buttons_name = []

    # Генерируем список порядкового номера пунктов меню в клавиатуре
    for i in range(0, len(menu_items)):
        list_index_menu_items.append(i)

    # Генерируем список наименований кнопок с пунктами меню
    for e in menu_items:
        status_menu_item = "  💤" if e["status"] == 0 else ""
        list_buttons_name.append(e["name"] + " " + status_menu_item)

    keyboard_menu_items = await get_inline_keyb_markup(
        list_names=list_buttons_name,
        list_data=list_index_menu_items,
        callback_str="delete_choose_menu_items",
        number_cols=2,
    )

    # Сохраняем название выбранного пункта и лист статусов пунктов меню (выбран или нет)
    await state.set_data({
        'list_index_menu_items': list_index_menu_items,
        'status_list': status_list,
        'menu_items': menu_items,
        'queue_text': msg_queue
    })

    await callback.message.edit_text(
        text=msg_queue + text_start_delete_menu_item,
        reply_markup=keyboard_menu_items,
        parse_mode="html"
    )


@rt.callback_query(StepsDeleteMenuItem.start_delete_menu_item, F.data.startswith("delete_choose_menu_items"))
async def change_delete_menu_items_list(callback: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()

    number_choose_menu_item = int(await get_callb_content(callback.data))
    new_data['status_list'][number_choose_menu_item] = 1 if new_data['status_list'][number_choose_menu_item] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': new_data['status_list'],
    })

    for i in range(0, len(new_data['menu_items'])):
        status_emoji = '' if new_data['status_list'][i] == 0 else '☑️'
        status_menu_item = "  💤" if new_data["menu_items"][i]["status"] == 0 else ""
        new_name_btn = " ".join([status_emoji, new_data["menu_items"][i]["name"], status_menu_item])
        list_names.append(new_name_btn)

    keyboard_menu_items = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=new_data['list_index_menu_items'],
        callback_str="delete_choose_menu_items",
        number_cols=2,
        add_keyb_to_start=keyb_str_delete_mi
    )

    await callback.message.edit_text(
        text=new_data['queue_text'] + text_start_delete_menu_item,
        reply_markup=keyboard_menu_items,
        parse_mode="html"
    )


# Предупреждающее сообщение --------------------------------------------------------------------------------------------
@rt.callback_query(StepsDeleteMenuItem.start_delete_menu_item, F.data == "next_step_delete_menu_item")
async def sure_msg_delete_menu_item(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsDeleteMenuItem.sure_msg_delete_item)
    state_data = await state.get_data()
    choose_items_names = []

    for i in range(0, len(state_data['menu_items'])):
        if state_data['status_list'][i] == 1:
            choose_items_names.append(state_data['menu_items'][i]['name'])

    sure_msg = await get_sure_delete_mi_msg(choose_items_names)

    await callback.message.edit_text(text=sure_msg, reply_markup=cf_key_end_delete_mi, parse_mode="html")


@rt.callback_query(StepsDeleteMenuItem.sure_msg_delete_item, F.data == "cancel_delete_menu_item")
async def cancel_delete_menu_item(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=text_stop_delete_menu_item, parse_mode="html")


@rt.callback_query(StepsDeleteMenuItem.sure_msg_delete_item, F.data == "end_delete_menu_item")
async def end_delete_menu_item(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()

    choose_items_id_list = []

    for i in range(0, len(state_data['menu_items'])):
        if state_data['status_list'][i] == 1:
            choose_items_id_list.append(state_data['menu_items'][i]['id'])

    await MenuItemApi.delete_menu_items_by_ids(choose_items_id_list)

    await callback.message.edit_text(text=text_end_delete_menu_item, parse_mode="html")