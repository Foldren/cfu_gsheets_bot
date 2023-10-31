from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsAdminFilter
from components.keyboards_components.generators import get_reply_keyb_markup_start
from components.keyboards_components.markups.reply import keyb_markup_operation_integration_banks
from components.texts.admins.change_menu import text_open_under_integration_banks_menu
from components.texts.users.change_menu import text_back_to_main_menu

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Интеграция с банками")
async def open_menu_operation_with_stats(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=text_open_under_integration_banks_menu,
        reply_markup=keyb_markup_operation_integration_banks
    )


@rt.message(F.text == "⬅️ Назад в главное меню")
async def open_menu_operation_with_stats(message: Message, state: FSMContext):
    await state.clear()
    await message.answer(
        text=text_back_to_main_menu,
        reply_markup=await get_reply_keyb_markup_start(message.from_user.id, "admin")
    )
