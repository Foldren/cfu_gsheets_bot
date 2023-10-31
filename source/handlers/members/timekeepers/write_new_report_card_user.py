from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsTimeKeeperFilter
from components.keyboards_components.generators import get_inline_keyb_markup
from components.texts.members.write_new_report_card_user import text_start_write_new_report_type_user
from microservices.redis_models.user import RedisUser
from microservices.sql_models_extends.user import UserExtend

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsTimeKeeperFilter(), F.chat.type == "private")
rt.callback_query.filter(IsTimeKeeperFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Табель")
async def start_write_new_report_type_user(message: Message, state: FSMContext, redis_users: RedisUser):
    await state.clear()
    admin_id = await redis_users.get_user_admin_id(message.from_user.id)
    users = await UserExtend.get_admin_users(admin_id, include_admin=True)
    stasuses = ["🔴 Не пришел:", "🟢 На работе:", "🔵 Ушел:"]
    keyboard_markup = await get_inline_keyb_markup(
        callback_str='report_card',
        number_cols=1,
        list_names=[f" {u['fullname'].split(' ')[1]} - {u['profession']}" for u in users],
        list_data=[u['chat_id'] for u in users]
    )
    await message.answer(text=text_start_write_new_report_type_user, reply_markup=keyboard_markup)

