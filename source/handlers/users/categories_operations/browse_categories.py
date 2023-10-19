from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsUserFilter, IsNotMainMenuMessage
from components.tools import get_msg_queue, get_callb_content, \
    get_str_format_queue
from components.keyboards_components.generators import get_inline_keyb_markup, get_inline_keyb_profit_cost, \
    get_inline_keyb_str_back_to_parent_items_u
from components.texts.users.write_category_to_bd import text_get_user_list_mi
from microservices.sql_models_extends.category import CategoryExtend
from states.user.steps_create_notes_to_bd import StepsWriteCategoriesToBd

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


# Вывод дочерних пунктов меню
@rt.callback_query(StepsWriteCategoriesToBd.set_queue_categories, F.data.startswith("user_menu_item"))
async def next_to_nested_categories_u(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteCategoriesToBd.set_queue_categories)

    message = callback.message
    selected_category_id = await get_callb_content(callback.data)
    selected_item = await CategoryExtend.get_by_id(selected_category_id)
    categories = await CategoryExtend.get_user_categories_by_parent_id(callback.from_user.id, parent_id=selected_item.id)
    queue = await get_str_format_queue(selected_category_id)
    msg_queue = '<b>Операция с категориями:</b> (шаг 3)\n\n' + await get_msg_queue(selected_item.level, selected_item.name, queue)

    dict_c_names_ids = {'names': [], "ids": []}

    # Заполняем дикт списки названиями кнопок и данными колбеков, пропускаем скрытые (id mi)
    for e in categories:
        if e['status'] == 1:
            dict_c_names_ids['names'].append(e['name'])
            dict_c_names_ids['ids'].append(e['id'])

    if dict_c_names_ids['names']:
        keyboard = await get_inline_keyb_markup(
            list_names=dict_c_names_ids['names'],
            list_data=dict_c_names_ids['ids'],
            callback_str="user_menu_item",
            number_cols=2,
            add_keyb_to_start=await get_inline_keyb_str_back_to_parent_items_u(selected_category_id)
        )

        await message.edit_text(text=msg_queue, reply_markup=keyboard, parse_mode="html")

    else:
        # Если последняя категория и это колбек, добавляем кнопки расход и доход
        keyboard = await get_inline_keyb_profit_cost(selected_category_id)
        await message.edit_text(text=msg_queue, reply_markup=keyboard, parse_mode="html")


# Возврат назад к родительским пунктам меню
@rt.callback_query(StepsWriteCategoriesToBd.set_queue_categories, F.data.startswith("back_to_upper_level_u"))
async def back_to_parent_categories_u(callback: CallbackQuery):
    selected_category_id = await get_callb_content(callback.data)
    selected_category = await CategoryExtend.get_by_id(selected_category_id)
    parent_category = await selected_category.parent
    parent_category_name = parent_category.name if parent_category is not None else None
    categories = await CategoryExtend.get_parent_categories_by_chat_id(selected_category_id, callback.message.chat.id)
    old_queue = await get_str_format_queue(selected_category_id)
    new_queue = old_queue[:old_queue.rfind('→') - 1]
    msg_queue = await get_msg_queue(selected_category.level-1, parent_category_name, new_queue)
    upper_level = categories[0]['parent_id'] is None
    final_msg = text_get_user_list_mi + msg_queue if upper_level else '<b>Операция с категориями:</b> (шаг 3)\n\n' + msg_queue
    selected_upper_item_id = selected_category.parent_id
    dict_mi_names_ids = {'names': [], "ids": []}

    # Заполняем дикт списки названиями кнопок и данными колбеков, пропускаем скрытые (id mi)
    for e in categories:
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

