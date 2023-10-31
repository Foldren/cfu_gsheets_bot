from aiogram import Router, Bot, F
from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeAllPrivateChats
from components.commands import main_commands
from components.filters import IsAdminFilter
from components.keyboards_components.generators import get_reply_keyb_markup_start
from components.text_generators.admins import get_text_start_admin

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


# Хэндлер на команду /start
@rt.message(Command(commands=["start", "restart"]), F.chat.type == "private")
async def start_admin(message: Message, state: FSMContext, bot_object: Bot):
    await state.clear()
    message_text = await get_text_start_admin(message.from_user.full_name)

    await bot_object.set_my_commands(commands=main_commands, scope=BotCommandScopeAllPrivateChats())
    await message.answer(message_text, reply_markup=await get_reply_keyb_markup_start(message.from_user.id, "admin"), parse_mode='html')
