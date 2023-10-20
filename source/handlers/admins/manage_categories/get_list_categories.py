from typing import Union
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F
from components.filters import IsAdminFilter
from components.texts.admins.manage_categories import text_get_list_categories
from microservices.sql_models_extends.category import CategoryExtend
from components.tools import get_msg_queue, \
    get_callb_content, get_str_format_queue
from components.keyboards_components.generators import get_inline_keyb_markup, get_inline_keyb_markup_empty, \
    get_inline_keyb_str_full
from states.admin.steps_manage_categories import StepsGetCategoriesList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


# Вывод дочерних пунктов меню
@rt.message(F.text == "Категории")
@rt.callback_query(StepsGetCategoriesList.get_list_categories, F.data.startswith("menu_item"))
async def next_to_nested_categories(callb_or_msg: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    await state.set_state(StepsGetCategoriesList.get_list_categories)

    # Проверка message или callback ------------------------------------------------------------------------------------
    if hasattr(callb_or_msg, "data"):
        main_category = False  # Проверяем главная ли это категория
        message = callb_or_msg.message  # Берем объект message

    else:
        main_category = True
        message = callb_or_msg  # Берем объект message

    # Проверка уровня меню ---------------------------------------------------------------------------------------------
    if main_category:
        selected_category_id = None
        categories = await CategoryExtend.get_user_upper_categories(callb_or_msg.from_user.id)
        msg_queue = await get_msg_queue(level=0)
    else:
        selected_category_id = await get_callb_content(callb_or_msg.data)
        selected_category = await CategoryExtend.get_by_id(selected_category_id)
        categories = await CategoryExtend.get_user_categories_by_parent_id(callb_or_msg.from_user.id, parent_id=selected_category.id)
        queue = await get_str_format_queue(selected_category_id)
        msg_queue = await get_msg_queue(selected_category.level, selected_category.name, queue)

    if categories:
        keyboard = await get_inline_keyb_markup(
            list_names=[(e["name"] + ("  💤" if e["status"] == 0 else "")) for e in categories],
            list_data=[e["id"] for e in categories],
            callback_str="menu_item" if categories[0]['level'] < 6 else "empty",
            number_cols=2,
            add_keyb_to_start=await get_inline_keyb_str_full(selected_category_id, upper=main_category)
        )
        if categories[0]['level'] == 5:
            msg_queue += "\n Вы достигли максимального уровня 🆙"

    else:
        keyboard = await get_inline_keyb_markup_empty(selected_category_id)

    if main_category and hasattr(callb_or_msg, "data"):
        await message.edit_text(text=text_get_list_categories + msg_queue, reply_markup=keyboard, parse_mode="html")
    elif main_category and not hasattr(callb_or_msg, "data"):
        await message.answer(text=text_get_list_categories + msg_queue, reply_markup=keyboard, parse_mode="html")
    else:
        await message.edit_text(text=f"<b>Категории</b>\n\n" + msg_queue, reply_markup=keyboard, parse_mode='html')


# Возврат назад к родительским пунктам меню
@rt.callback_query(StepsGetCategoriesList.get_list_categories, F.data.startswith("back_to_upper_level"))
async def back_to_parent_categories(callback: CallbackQuery):
    selected_category_id = await get_callb_content(callback.data)
    selected_category = await CategoryExtend.get_by_id(selected_category_id)
    categories = await CategoryExtend.get_parent_categories_by_chat_id(selected_category_id, callback.message.chat.id)
    old_queue = await get_str_format_queue(selected_category_id)
    new_queue = old_queue[:old_queue.rfind('→')-1]
    is_main_category = await selected_category.parent
    parent_category_name = is_main_category.name if is_main_category is not None else None
    msg_queue = await get_msg_queue(selected_category.level-1, parent_category_name, new_queue)
    is_main_category = categories[0]['parent_id'] is None

    if categories[0]['level'] == 1:
        final_msg = text_get_list_categories + msg_queue
    else:
        final_msg = f"<b>Категории</b>\n\n" + msg_queue

    selected_upper_category_id = selected_category.parent_id

    keyboard = await get_inline_keyb_markup(
        list_names=[(e["name"] + ("  💤" if e["status"] == 0 else "")) for e in categories],
        list_data=[e["id"] for e in categories],
        callback_str="menu_item",
        number_cols=2,
        add_keyb_to_start=await get_inline_keyb_str_full(selected_upper_category_id, upper=is_main_category)
    )

    await callback.message.edit_text(text=final_msg, reply_markup=keyboard, parse_mode='html')

