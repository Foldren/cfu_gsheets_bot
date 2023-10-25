from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter, IsNotMainMenuMessage
from components.keyboards_components.markups.inline import keyb_markup_pass_check_load
from components.keyboards_components.generators import get_inline_keyb_markup
from components.texts.users.write_category_to_bd import text_start_add_mi_to_bd, text_choose_bank, \
    text_invalid_volume_operation, text_send_check_photo, text_invalid_check_photo
from components.tools import get_callb_content, add_new_note_to_bd_handler_algorithm, \
    get_str_format_queue
from microservices.google_api.google_drive import GoogleDrive
from microservices.google_api.google_table import GoogleTable
from microservices.redis_models.wallets import RedisUserWallets
from states.user.steps_create_notes_to_bd import StepsWriteCategoriesToBd

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsWriteCategoriesToBd.set_queue_categories,
                   (F.data.startswith("profit_item") | F.data.startswith("cost_item")))
async def start_write_new_note_to_bd(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteCategoriesToBd.set_volume_operation)

    category_id = await get_callb_content(callback.data)
    queue = await get_str_format_queue(category_id)

    await state.update_data({
        'item_queue': queue,
        'organization_id': category_id,
        'operation_type': 'cost' if "cost_item" in callback.data else "profit"
    })

    await callback.message.edit_text(text=text_start_add_mi_to_bd, parse_mode="html")


@rt.message(StepsWriteCategoriesToBd.set_volume_operation)
async def choose_bank(message: Message, state: FSMContext, redis_wallets: RedisUserWallets):
    await state.set_state(StepsWriteCategoriesToBd.choose_bank)

    try:
        volume_op = int(message.text)
    except Exception:
        await state.set_state(StepsWriteCategoriesToBd.set_volume_operation)
        await message.answer(text=text_invalid_volume_operation, parse_mode="html")
        return

    wallets_list = await redis_wallets.get_wallets_list(message.from_user.id)

    keyboard = await get_inline_keyb_markup(
        list_names=wallets_list,
        list_data=wallets_list,
        callback_str="bank_operation",
        number_cols=2,
    )

    await state.update_data({
        'volume_operation': volume_op,
    })

    await message.answer(text=text_choose_bank, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteCategoriesToBd.choose_bank)
async def load_or_pass_load_check(callback: CallbackQuery, state: FSMContext, bot_object: Bot,
                                  gt_object: GoogleTable, gd_object: GoogleDrive):
    st_data = await state.get_data()
    selected_bank = await get_callb_content(callback.data)

    await state.update_data({
        'payment_method': selected_bank
    })

    if st_data['sender'] == "me" and st_data['operation_type'] == 'cost':
        await state.set_state(StepsWriteCategoriesToBd.load_check)
        await callback.message.edit_text(text=text_send_check_photo, reply_markup=keyb_markup_pass_check_load, parse_mode="html")
    else:
        await add_new_note_to_bd_handler_algorithm(callback.message, state, bot_object, gt_object, gd_object)


@rt.callback_query(StepsWriteCategoriesToBd.load_check, F.data.startswith("pass_check_load"))
async def end_write_new_note_pass_load_check(callback: CallbackQuery, state: FSMContext,
                                             bot_object: Bot, gt_object: GoogleTable, gd_object: GoogleDrive):
    await add_new_note_to_bd_handler_algorithm(callback.message, state, bot_object, gt_object, gd_object)


@rt.message(StepsWriteCategoriesToBd.load_check)
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









