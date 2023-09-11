from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter
from components.users.texts import text_start_add_mi_to_bd, text_invalid_volume_operation, text_send_check_photo, \
    text_invalid_check_photo, text_choose_bank
from components.tools import get_callb_content, get_inline_keyb_markup, add_new_note_to_bd_handler_algorithm, \
    get_str_format_queue
from config import BANKS_UPRAVLYAIKA
from services.google_api.google_drive import GoogleDrive
from services.google_api.google_table import GoogleTable
from states.steps_create_notes_to_bd import BrowseMenuItems, WriteMenuItemsToBd

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter())
rt.callback_query.filter(IsUserFilter())


@rt.callback_query(BrowseMenuItems.get_list_menu_items,
                   (F.data.startswith("profit_item") | F.data.startswith("cost_item")))
async def start_write_new_note_to_bd(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(WriteMenuItemsToBd.set_volume_operation)

    item_id = await get_callb_content(callback.data)
    queue = await get_str_format_queue(item_id)

    await state.set_data({
        'item_queue': queue,
        'item_id': item_id,
        'operation_type': 'cost' if "cost_item" in callback.data else "profit"
    })

    await callback.message.edit_text(text=text_start_add_mi_to_bd, parse_mode="html")


@rt.message(WriteMenuItemsToBd.set_volume_operation)
async def choose_bank(message: Message, state: FSMContext):
    await state.set_state(WriteMenuItemsToBd.choose_bank)

    try:
        volume_op = int(message.text)
    except Exception:
        await state.set_state(WriteMenuItemsToBd.set_volume_operation)
        await message.answer(text=text_invalid_volume_operation, parse_mode="html")
        return

    keyboard = await get_inline_keyb_markup(
        list_names=BANKS_UPRAVLYAIKA,
        list_data=BANKS_UPRAVLYAIKA,
        callback_str="bank_operation",
        number_cols=2,
    )

    await state.update_data({
        'volume_operation': volume_op,
    })

    await message.answer(text=text_choose_bank, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(WriteMenuItemsToBd.choose_bank)
async def load_check(callback: CallbackQuery, state: FSMContext):
    await state.set_state(WriteMenuItemsToBd.load_check)

    selected_bank = await get_callb_content(callback.data)

    await state.update_data({
        'payment_method': selected_bank
    })

    await callback.message.edit_text(text=text_send_check_photo, parse_mode="html")


@rt.message(WriteMenuItemsToBd.load_check)
async def end_write_new_note(message: Message, state: FSMContext, bot_object: Bot,
                             gt_object: GoogleTable, gd_object: GoogleDrive):
    if message.photo:
        file_id = message.photo[-1].file_id
        await add_new_note_to_bd_handler_algorithm(message, state, bot_object, gt_object, gd_object, file_id)

    elif message.document:
        if message.document.mime_type[:5] == 'image':
            file_id = message.document.file_id
            await add_new_note_to_bd_handler_algorithm(message, state, bot_object, gt_object, gd_object, file_id)
        else:
            await message.answer(text=text_invalid_check_photo)

    else:
        await message.answer(text=text_invalid_check_photo)









