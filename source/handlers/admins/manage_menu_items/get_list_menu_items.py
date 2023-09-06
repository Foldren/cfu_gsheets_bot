from typing import Union
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from components.filters import IsAdminFilter
from components.texts import text_get_list_categories
from services.database_extends.menu_item import MenuItemApi
from components.tools import get_inline_keyb_markup, get_msg_queue, \
    get_callb_content, get_inline_keyb_markup_empty, \
    get_inline_keyb_str_full
from states.steps_manage_menu_items import StepsGetListMenu

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


# Вывод дочерних пунктов меню
@rt.message(F.text == "Меню")
@rt.callback_query(StepsGetListMenu.get_list_menu_items, F.data.startswith("menu_item"))
async def next_to_nested_items(callb_or_msg: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    await state.set_state(StepsGetListMenu.get_list_menu_items)

    # Проверка message или callback ------------------------------------------------------------------------------------
    if hasattr(callb_or_msg, "data"):
        upper_menu = False  # Проверяем верхний ли это уровень
        message = callb_or_msg.message  # Берем объект message

    else:
        upper_menu = True
        message = callb_or_msg  # Берем объект message

    # Проверка уровня меню ---------------------------------------------------------------------------------------------
    if upper_menu:
        selected_item_id = None
        menu_items = await MenuItemApi.get_user_upper_items(callb_or_msg.from_user.id)
        msg_queue = await get_msg_queue(level=0)
    else:
        selected_item_id = await get_callb_content(callb_or_msg.data)
        selected_item = await MenuItemApi.get_by_id(selected_item_id)
        menu_items = await MenuItemApi.get_user_items_by_parent_id(callb_or_msg.from_user.id, parent_id=selected_item.id)
        msg_queue = await get_msg_queue(selected_item.level, selected_item.name, selected_item.queue)

    if menu_items:
        keyboard = await get_inline_keyb_markup(
            list_names=[(e["name"] + ("  💤" if e["status"] == 0 else "")) for e in menu_items],
            list_data=[e["id"] for e in menu_items],
            callback_str="menu_item" if menu_items[0]['level'] < 6 else "empty",
            number_cols=2,
            add_keyb_to_start=await get_inline_keyb_str_full(selected_item_id, upper=upper_menu)
        )
        if menu_items[0]['level'] == 6:
            msg_queue += "\n Вы достигли максимального уровня 🆙"

    else:
        keyboard = await get_inline_keyb_markup_empty(selected_item_id)

    if upper_menu and hasattr(callb_or_msg, "data"):
        await message.edit_text(text=text_get_list_categories + msg_queue, reply_markup=keyboard, parse_mode="html")
    if upper_menu and not hasattr(callb_or_msg, "data"):
        await message.answer(text=text_get_list_categories + msg_queue, reply_markup=keyboard, parse_mode="html")
    else:
        await message.edit_text(text=msg_queue, reply_markup=keyboard, parse_mode='html')


# Возврат назад к родительским пунктам меню
@rt.callback_query(StepsGetListMenu.get_list_menu_items, F.data.startswith("back_to_upper_level"))
async def back_to_parent_items(callback: CallbackQuery):
    selected_item_id = await get_callb_content(callback.data)
    selected_item = await MenuItemApi.get_by_id(selected_item_id)
    menu_items = await MenuItemApi.get_parent_items(selected_item_id)
    new_queue = selected_item.queue[:selected_item.queue.rfind('→')-1]
    parent_item = await selected_item.parent
    parent_item_name = parent_item.name if parent_item is not None else None
    msg_queue = await get_msg_queue(selected_item.level-1, parent_item_name, new_queue)
    upper_level = menu_items[0]['parent_id'] is None
    final_msg = text_get_list_categories + msg_queue if upper_level else msg_queue
    selected_upper_item_id = selected_item.parent_id

    keyboard = await get_inline_keyb_markup(
        list_names=[(e["name"] + ("  💤" if e["status"] == 0 else "")) for e in menu_items],
        list_data=[e["id"] for e in menu_items],
        callback_str="menu_item",
        number_cols=2,
        add_keyb_to_start=await get_inline_keyb_str_full(selected_upper_item_id, upper=upper_level)
    )

    await callback.message.edit_text(text=final_msg, reply_markup=keyboard, parse_mode='html')

