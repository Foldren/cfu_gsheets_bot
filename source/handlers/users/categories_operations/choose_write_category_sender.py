from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter
from components.keyboards_components.configurations.inline import cf_keyb_choose_write_menu_sender
from components.tools import get_callb_content, get_msg_queue
from components.keyboards_components.generators import get_inline_keyb_markup
from components.texts.users.write_category_to_bd import text_get_user_list_mi, text_no_menu_items_u, \
    text_choose_sender_write_item
from services.sql_models_extends.category import CategoryExtend
from states.user.steps_create_notes_to_bd import StepsWriteCategoriesToBd

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter())
rt.callback_query.filter(IsUserFilter())


@rt.message(F.text == "Операция с категориями")
async def start_choose_write_category_sender(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StepsWriteCategoriesToBd.set_sender)
    await message.answer(text=text_choose_sender_write_item, reply_markup=cf_keyb_choose_write_menu_sender, parse_mode="html")


@rt.callback_query(StepsWriteCategoriesToBd.set_sender, F.data.startswith("choose_write_menu_sender"))
async def end_choose_write_category_sender(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteCategoriesToBd.set_queue_categories)

    callb_data = await get_callb_content(callback.data)

    await state.set_data({
        'sender': callb_data
    })

    await state.set_state(StepsWriteCategoriesToBd.set_queue_categories)

    message = callback.message
    categories = await CategoryExtend.get_user_upper_categories(callback.message.chat.id)
    msg_queue = await get_msg_queue(level=0)
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
            number_cols=2
        )

        await message.edit_text(
            text=text_get_user_list_mi + msg_queue,
            reply_markup=keyboard,
            parse_mode="html"
        )
    else:
        # Если это кнопка "новая запись" и нет элементов
        await message.edit_text(text=text_no_menu_items_u, parse_mode="html")


