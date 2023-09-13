from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter
from components.keyboards import cf_keyb_choose_write_menu_sender
from components.tools import get_callb_content, get_msg_queue, \
    get_inline_keyb_markup
from components.users.texts import text_choose_sender_write_item, text_get_user_list_mi, text_no_menu_items_u
from services.models_extends.menu_item import MenuItemApi
from states.user.steps_create_notes_to_bd import WriteMenuItemsToBd

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter())
rt.callback_query.filter(IsUserFilter())


@rt.message(F.text == "Операция с категориями")
async def choose_write_menu_item_sender(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(WriteMenuItemsToBd.set_sender)
    await message.answer(text=text_choose_sender_write_item, reply_markup=cf_keyb_choose_write_menu_sender, parse_mode="html")


@rt.callback_query(WriteMenuItemsToBd.set_sender, F.data.startswith("choose_write_menu_sender"))
async def choose_write_menu_item_sender(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WriteMenuItemsToBd.set_queue_menu_items)

    callb_data = await get_callb_content(callback.data)

    await state.set_data({
        'sender': callb_data
    })

    await state.set_state(WriteMenuItemsToBd.set_queue_menu_items)

    message = callback.message
    menu_items = await MenuItemApi.get_user_upper_items(callback.message.chat.id)
    msg_queue = await get_msg_queue(level=0)
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


