from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsAdminFilter
from components.keyboards import cf_key_start_admin, keyb_start_user_admin, keyb_start_admin
from services.database_extends.user import UserApi

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


@rt.message(((F.text == "Режим: Админ 👨‍💼") or (F.text == "Режим: Юзер 🙎‍♂️")))
async def change_mode(message: Message, state: FSMContext):
    await state.clear()
    admin_info = await UserApi.get_admin_info(message.from_user.id)
    admin_mode = admin_info.admin_mode

    if admin_mode:
        keyboard = keyb_start_user_admin
    else:
        keyboard = keyb_start_admin

    await UserApi.invert_mode(message.from_user.id)

    await message.answer(message_text, reply_markup=keyboard, parse_mode='html')
