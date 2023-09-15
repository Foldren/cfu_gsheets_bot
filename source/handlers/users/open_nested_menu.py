from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsUserFilter
from components.keyboards_components.configurations.reply import cf_keyb_start_user, \
    cf_keyb_start_user_admin, cf_keyb_operation_under_stats, cf_keyb_wallets
from components.texts.users.change_menu import text_open_under_stats_menu, text_open_wallets_menu, \
    text_back_to_main_menu
from services.sql_models_extends.user import UserExtend

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter())
rt.callback_query.filter(IsUserFilter())


@rt.message(F.text == "Операция с подотчетами")
async def open_menu_operation_with_stats(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=text_open_under_stats_menu, reply_markup=cf_keyb_operation_under_stats)


@rt.message(F.text == "Кошельки")
async def open_menu_wallets(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=text_open_wallets_menu, reply_markup=cf_keyb_wallets)


@rt.message(F.text == "⬅️ Назад в главное меню")
async def open_menu_operation_with_stats(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.chat.id
    admin_id = await UserExtend.get_user_admin_id(user_id)

    if user_id == admin_id:
        keyboard = cf_keyb_start_user_admin
    else:
        keyboard = cf_keyb_start_user

    await message.answer(text=text_back_to_main_menu, reply_markup=keyboard)
