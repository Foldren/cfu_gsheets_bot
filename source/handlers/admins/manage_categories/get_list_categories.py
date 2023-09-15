from typing import Union
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.texts.admins.manage_categories import text_get_list_ur_faces, text_get_list_categories
from services.sql_models_extends.category import CategoryExtend
from components.tools import get_msg_queue, \
    get_callb_content, get_str_format_queue
from components.keyboards_components.generators import get_inline_keyb_markup, get_inline_keyb_markup_empty, \
    get_inline_keyb_str_full
from states.admin.steps_manage_categories import StepsGetCategoriesList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


# Вывод дочерних пунктов меню
@rt.message(F.text == "Меню")
@rt.callback_query(StepsGetCategoriesList.get_list_categories, F.data.startswith("menu_item"))
async def next_to_nested_items(callb_or_msg: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    await state.set_state(StepsGetCategoriesList.get_list_categories)

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
        selected_item = None
        menu_items = await CategoryExtend.get_user_upper_categories(callb_or_msg.from_user.id)
        msg_queue = await get_msg_queue(level=0)
    else:
        selected_item_id = await get_callb_content(callb_or_msg.data)
        selected_item = await CategoryExtend.get_by_id(selected_item_id)
        menu_items = await CategoryExtend.get_user_categories_by_parent_id(callb_or_msg.from_user.id, parent_id=selected_item.id)
        queue = await get_str_format_queue(selected_item_id)
        msg_queue = await get_msg_queue(selected_item.level, selected_item.name, queue)

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
        await message.edit_text(text=text_get_list_ur_faces + msg_queue, reply_markup=keyboard, parse_mode="html")
    elif upper_menu and not hasattr(callb_or_msg, "data"):
        await message.answer(text=text_get_list_ur_faces + msg_queue, reply_markup=keyboard, parse_mode="html")
    elif selected_item_id is not None:
        if selected_item.level == 1:
            await message.edit_text(text=text_get_list_categories + msg_queue, reply_markup=keyboard, parse_mode="html")
        else:
            await message.edit_text(text=msg_queue, reply_markup=keyboard, parse_mode='html')


# Возврат назад к родительским пунктам меню
@rt.callback_query(StepsGetCategoriesList.get_list_categories, F.data.startswith("back_to_upper_level"))
async def back_to_parent_items(callback: CallbackQuery):
    selected_item_id = await get_callb_content(callback.data)
    selected_item = await CategoryExtend.get_by_id(selected_item_id)
    menu_items = await CategoryExtend.get_parent_categories_by_chat_id(selected_item_id, callback.message.chat.id)
    old_queue = await get_str_format_queue(selected_item_id)
    new_queue = old_queue[:old_queue.rfind('→')-1]
    parent_item = await selected_item.parent
    parent_item_name = parent_item.name if parent_item is not None else None
    msg_queue = await get_msg_queue(selected_item.level-1, parent_item_name, new_queue)
    upper_level = menu_items[0]['parent_id'] is None

    if menu_items[0]['level'] == 1:
        final_msg = text_get_list_ur_faces + msg_queue
    elif menu_items[0]['level'] == 2:
        final_msg = text_get_list_categories + msg_queue
    else:
        final_msg = msg_queue

    selected_upper_item_id = selected_item.parent_id

    keyboard = await get_inline_keyb_markup(
        list_names=[(e["name"] + ("  💤" if e["status"] == 0 else "")) for e in menu_items],
        list_data=[e["id"] for e in menu_items],
        callback_str="menu_item",
        number_cols=2,
        add_keyb_to_start=await get_inline_keyb_str_full(selected_upper_item_id, upper=upper_level)
    )

    await callback.message.edit_text(text=final_msg, reply_markup=keyboard, parse_mode='html')

