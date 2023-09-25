from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.text_generators.admins import get_text_start_admin
from components.texts.admins.manage_users import text_start_admin_user
from components.filters import IsAdminFilter
from components.keyboards_components.configurations.reply import cf_keyb_start_admin, \
    cf_keyb_start_user_admin
from services.redis_models.user import RedisUser

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.chat.type == "private")


@rt.message(F.text.in_({'Режим: Админ 👨‍💼', 'Режим: Юзер 🙎‍♂️'}))
async def change_mode(message: Message, state: FSMContext, redis_users: RedisUser):
    await state.clear()
    admin_status = await redis_users.get_user_status(message.chat.id, invert=True)
    await redis_users.set_admin_status(message.chat.id, admin_status)

    if admin_status == 0:
        keyboard = cf_keyb_start_user_admin
        message_text = text_start_admin_user
    else:
        keyboard = cf_keyb_start_admin
        message_text = await get_text_start_admin(message.chat.full_name)

    await message.answer(message_text, reply_markup=keyboard, parse_mode='html')
