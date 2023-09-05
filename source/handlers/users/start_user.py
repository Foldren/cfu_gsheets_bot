from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router
from components.filters import IsUserFilter
from components.keyboards import cf_keyb_start_user

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter())
rt.callback_query.filter(IsUserFilter())


# Хэндлер на команду /start
@rt.message(Command(commands=["start"]))
async def start_user(message: Message, state: FSMContext):
    await state.clear()

    message_text = f"Здравствуйте, юзер <b>{message.from_user.full_name}</b>!👋\n\n" \
                   f"<code>Рабочие кнопки бота Управляйки</code> ⚙️ :\n\n" \
                   f"1️⃣️ <b>Новая запись 🖊</b> - создайте и добавьте новую запись в отчет (лист БД), выбирая нужные " \
                   f"категории для позиции в отчете."

    await message.answer(message_text, reply_markup=cf_keyb_start_user, parse_mode='html')
