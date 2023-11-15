from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsAdminFilter
from components.keyboards_components.generators import get_reply_keyb_markup_start
from components.text_generators.admins import get_text_start_admin
from components.texts.admins.manage_users import text_start_admin_user
from config import SUPER_ADMINS_CHAT_ID
from microservices.redis_models.user import RedisUser

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.message(F.text.in_({'Режим: Админ 👨‍💼', 'Режим: Юзер 🙎‍♂️', 'Режим: Суперадмин 👨‍💻'}))
async def change_mode(message: Message, state: FSMContext, redis_users: RedisUser):
    await state.clear()

    if message.text == 'Режим: Админ 👨‍💼':
        admin_status = 0

    if message.text == 'Режим: Юзер 🙎‍♂️' and (message.from_user.id in SUPER_ADMINS_CHAT_ID):
        admin_status = 2
    elif message.text == 'Режим: Юзер 🙎‍♂️' and (message.from_user.id not in SUPER_ADMINS_CHAT_ID):
        admin_status = 1

    if message.text == 'Режим: Суперадмин 👨‍💻' and (message.from_user.id in SUPER_ADMINS_CHAT_ID):
        admin_status = 1
    elif message.text == 'Режим: Суперадмин 👨‍💻' and (message.from_user.id not in SUPER_ADMINS_CHAT_ID):
        return

    await redis_users.set_admin_mode(message.chat.id, admin_status)

    if admin_status == 0:
        keyboard = await get_reply_keyb_markup_start(message.from_user.id, "admin_user")
        message_text = text_start_admin_user
    elif admin_status == 1:
        keyboard = await get_reply_keyb_markup_start(message.from_user.id, "admin")
        message_text = await get_text_start_admin(message.chat.full_name)
    else:
        keyboard = await get_reply_keyb_markup_start(message.from_user.id, "superadmin")
        message_text = "👨‍💻 Включен режим суперадмина"

    await message.answer(message_text, reply_markup=keyboard, parse_mode='html')
