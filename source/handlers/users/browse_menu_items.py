from typing import Union
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from components.filters import IsUserFilter
from components.texts import text_get_user_list_mi, text_no_menu_items_u
from services.database_extends.menu_item import MenuItemApi
from components.tools import get_inline_keyb_markup, get_msg_queue, get_callb_content, \
    get_inline_keyb_profit_cost, answer_or_edit_message, get_inline_keyb_str_back_to_parent_items_u
from states.steps_create_notes_to_bd import BrowseMenuItems

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter())
rt.callback_query.filter(IsUserFilter())


# Вывод дочерних пунктов меню
@rt.message(F.text == "Новая запись 🖊")
@rt.callback_query(BrowseMenuItems.get_list_menu_items, F.data.startswith("user_menu_item"))
async def next_to_nested_items_u(callb_or_msg: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    await state.set_state(BrowseMenuItems.get_list_menu_items)

    # Проверка message или callback ------------------------------------------------------------------------------------
    if hasattr(callb_or_msg, "data"):
        main_menu = False  # Проверяем верхний ли это уровень
        message = callb_or_msg.message  # Берем объект message

    else:
        main_menu = True
        message = callb_or_msg  # Берем объект message

    # Проверка уровня меню ---------------------------------------------------------------------------------------------
    if main_menu:
        selected_item_id = None
        menu_items = await MenuItemApi.get_user_upper_items(callb_or_msg.from_user.id)
        msg_queue = await get_msg_queue(level=1)
    else:
        selected_item_id = await get_callb_content(callb_or_msg.data)
        selected_item = await MenuItemApi.get_by_id(selected_item_id)
        menu_items = await MenuItemApi.get_user_items_by_parent_id(callb_or_msg.from_user.id, parent_id=selected_item.id)
        msg_queue = await get_msg_queue(selected_item.level + 1, selected_item.name, selected_item.queue)

    dict_mi_names_ids = {'names': [], "ids": []}

    # Заполняем дикт списки названиями кнопок и данными колбеков, пропускаем скрытые (id mi)
    for e in menu_items:
        if e['status'] == 1:
            dict_mi_names_ids['names'].append(e['name'])
            dict_mi_names_ids['ids'].append(e['id'])

    if dict_mi_names_ids['names']:
        keyboard = await get_inline_keyb_markup(
            list_names=dict_mi_names_ids['names'],
            list_data=dict_mi_names_ids['ids'],
            callback_str="user_menu_item",
            number_cols=2,
            add_keyb_to_start=None if main_menu else await get_inline_keyb_str_back_to_parent_items_u(selected_item_id)
        )

        await answer_or_edit_message(
            message=message,
            flag_answer=main_menu,
            text=text_get_user_list_mi if main_menu else "" + msg_queue,
            keyboard=keyboard
        )

    else:
        if hasattr(callb_or_msg, "data"):
            # Если последняя категория и это колбек, добавляем кнопки расход и доход
            keyboard = await get_inline_keyb_profit_cost(selected_item_id)
            await message.edit_text(text=msg_queue, reply_markup=keyboard, parse_mode="html")
        else:
            # Если это кнопка "новая запись" и нет элементов
            await message.answer(text=text_no_menu_items_u, parse_mode="html")


# Возврат назад к родительским пунктам меню
@rt.callback_query(BrowseMenuItems.get_list_menu_items, F.data.startswith("back_to_upper_level_u"))
async def back_to_parent_items_u(callback: CallbackQuery):
    selected_item_id = await get_callb_content(callback.data)
    selected_item = await MenuItemApi.get_by_id(selected_item_id)
    menu_items = await MenuItemApi.get_parent_items_by_chat_id(selected_item_id, callback.message.chat.id)
    new_queue = selected_item.queue[:selected_item.queue.rfind('→')-1]
    msg_queue = await get_msg_queue(selected_item.level, selected_item.name, new_queue)
    upper_level = menu_items[0]['parent_id'] is None
    final_msg = text_get_user_list_mi + msg_queue if upper_level else msg_queue
    selected_upper_item_id = selected_item.parent_id
    dict_mi_names_ids = {'names': [], "ids": []}

    # Заполняем дикт списки названиями кнопок и данными колбеков, пропускаем скрытые (id mi)
    for e in menu_items:
        if e['status'] == 1:
            dict_mi_names_ids['names'].append(e['name'])
            dict_mi_names_ids['ids'].append(e['id'])

    keyb_str = None if upper_level else await get_inline_keyb_str_back_to_parent_items_u(selected_upper_item_id)

    keyboard = await get_inline_keyb_markup(
        list_names=dict_mi_names_ids['names'],
        list_data=dict_mi_names_ids['ids'],
        callback_str="user_menu_item",
        number_cols=2,
        add_keyb_to_start=keyb_str
    )

    await callback.message.edit_text(text=final_msg, reply_markup=keyboard, parse_mode='html')

