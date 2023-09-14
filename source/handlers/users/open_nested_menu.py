from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsUserFilter
from components.keyboards import cf_keyb_operation_under_stats, cf_keyb_start_user_admin, cf_keyb_start_user, \
    cf_keyb_operation_stats, cf_keyb_wallets
from components.users.texts import text_open_stats_menu, text_back_to_main_menu, text_open_wallets_menu, \
    text_open_under_stats_menu
from services.models_extends.user import UserApi

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


@rt.message(F.text == "Отчеты")
async def open_menu_stats(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(text=text_open_stats_menu, reply_markup=cf_keyb_operation_stats)


@rt.message(F.text == "⬅️ Назад в главное меню")
async def open_menu_operation_with_stats(message: Message, state: FSMContext):
    await state.clear()

    user_id = message.chat.id
    admin_id = await UserApi.get_user_admin_id(user_id)

    if user_id == admin_id:
        keyboard = cf_keyb_start_user_admin
    else:
        keyboard = cf_keyb_start_user

    await message.answer(text=text_back_to_main_menu, reply_markup=keyboard)
