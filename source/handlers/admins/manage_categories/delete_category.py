from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.markups.inline import keyb_markup_end_delete_mi
from components.keyboards_components.inline_strings import keyb_str_delete_mi
from components.texts.admins.manage_categories import text_start_delete_menu_item, text_stop_delete_menu_item, \
    text_end_delete_menu_item
from components.tools import get_callb_content, get_msg_queue, generate_zero_array, get_sure_delete_mi_msg, get_str_format_queue
from components.keyboards_components.generators import get_inline_keyb_markup
from microservices.sql_models_extends.category import CategoryExtend
from states.admin.steps_manage_categories import StepsGetCategoriesList, StepsDeleteCategories

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetCategoriesList.get_list_categories,
                   F.data.startswith("delete_menu_items") | (F.data == 'delete_upper_menu_items'))
async def start_delete_category(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsDeleteCategories.start_delete_categories)

    # Проверка на верхнее меню
    if "delete_menu_items" in callback.data:
        parent_category_id = await get_callb_content(callback.data)
        parent_category = await CategoryExtend.get_by_id(parent_category_id)
        level_category = parent_category.level
        name_category = parent_category.name
        queue_category = await get_str_format_queue(parent_category_id)
    else:
        parent_category_id = None
        level_category = 0
        name_category = "Юр. Лица"
        queue_category = ""

    msg_queue = await get_msg_queue(level=level_category, selected_item_name=name_category, queue=queue_category)

    categories = await CategoryExtend.get_user_categories_by_parent_id(
        user_id=callback.message.chat.id,
        parent_id=parent_category_id
    )

    status_list = await generate_zero_array(len(categories))
    list_index_categories = []
    list_buttons_name = []

    # Генерируем список порядкового номера пунктов меню в клавиатуре
    for i in range(0, len(categories)):
        list_index_categories.append(i)

    # Генерируем список наименований кнопок с пунктами меню
    for e in categories:
        status_category = "  💤" if e["status"] == 0 else ""
        list_buttons_name.append(e["name"] + " " + status_category)

    keyboard_categories = await get_inline_keyb_markup(
        list_names=list_buttons_name,
        list_data=list_index_categories,
        callback_str="delete_choose_menu_items",
        number_cols=2,
    )

    # Сохраняем название выбранного пункта и лист статусов пунктов меню (выбран или нет)
    await state.set_data({
        'list_index_categories': list_index_categories,
        'status_list': status_list,
        'child_categories': categories,
        'queue_text': msg_queue
    })

    await callback.message.edit_text(
        text=f"<b>Удаление категорий</b>\n\n" + msg_queue + text_start_delete_menu_item,
        reply_markup=keyboard_categories,
        parse_mode="html"
    )


@rt.callback_query(StepsDeleteCategories.start_delete_categories, F.data.startswith("delete_choose_menu_items"))
async def change_delete_categories_list(callback: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()

    number_choose_category = int(await get_callb_content(callback.data))
    new_data['status_list'][number_choose_category] = 1 if new_data['status_list'][number_choose_category] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': new_data['status_list'],
    })

    for i in range(0, len(new_data['child_categories'])):
        status_emoji = '' if new_data['status_list'][i] == 0 else '☑️'
        status_category = "  💤" if new_data["child_categories"][i]["status"] == 0 else ""
        new_name_btn = " ".join([status_emoji, new_data["child_categories"][i]["name"], status_category])
        list_names.append(new_name_btn)

    keyboard_categories = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=new_data['list_index_categories'],
        callback_str="delete_choose_menu_items",
        number_cols=2,
        add_keyb_to_start=keyb_str_delete_mi
    )

    await callback.message.edit_text(
        text=f"<b>Удаление категорий</b>\n\n" + new_data['queue_text'] + text_start_delete_menu_item,
        reply_markup=keyboard_categories,
        parse_mode="html"
    )


# Предупреждающее сообщение --------------------------------------------------------------------------------------------
@rt.callback_query(StepsDeleteCategories.start_delete_categories, F.data == "next_step_delete_menu_item")
async def sure_msg_delete_categories(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsDeleteCategories.sure_msg_delete_categories)
    state_data = await state.get_data()
    choose_categories_names = []

    for i in range(0, len(state_data['child_categories'])):
        if state_data['status_list'][i] == 1:
            choose_categories_names.append(state_data['child_categories'][i]['name'])

    sure_msg = await get_sure_delete_mi_msg(choose_categories_names)

    await callback.message.edit_text(text=sure_msg, reply_markup=keyb_markup_end_delete_mi, parse_mode="html")


@rt.callback_query(StepsDeleteCategories.sure_msg_delete_categories, F.data == "cancel_delete_menu_item")
async def cancel_delete_categories(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=text_stop_delete_menu_item, parse_mode="html")


@rt.callback_query(StepsDeleteCategories.sure_msg_delete_categories, F.data == "end_delete_menu_item")
async def end_delete_categories(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()

    choose_categories_id_list = []

    for i in range(0, len(state_data['child_categories'])):
        if state_data['status_list'][i] == 1:
            choose_categories_id_list.append(state_data['child_categories'][i]['id'])

    await CategoryExtend.delete_categories_by_ids(choose_categories_id_list)

    await callback.message.edit_text(text=text_end_delete_menu_item, parse_mode="html")