from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router
from components.text_generators.admins import get_text_start_admin
from components.filters import IsAdminFilter
from components.keyboards_components.configurations.reply import cf_keyb_start_admin

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


# Хэндлер на команду /start
@rt.message(Command(commands=["start"]))
async def start_admin(message: Message, state: FSMContext):
    await state.clear()

    message_text = await get_text_start_admin(message.from_user.full_name)

    await message.answer(message_text, reply_markup=cf_keyb_start_admin, parse_mode='html')
