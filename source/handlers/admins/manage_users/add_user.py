from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsAdminFilter
from components.admins.texts import text_start_add_user, text_end_add_user, text_user_exists
from components.tools import get_msg_user_data
from services.models_extends.user import UserApi
from services.redis_extends.registrations import RedisRegistration
from states.admin.steps_manage_users import StepsGetListUsers, StepsAddUser

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


@rt.callback_query(StepsGetListUsers.get_list_users, F.data == "add_user")
async def start_add_user(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsAddUser.start_add_user)
    await callback.message.edit_text(text=text_start_add_user, parse_mode="html")


@rt.message(StepsAddUser.start_add_user)
async def end_add_user(message: Message, state: FSMContext, redis_regs: RedisRegistration):
    await state.clear()

    msg_data = await get_msg_user_data(message.text)

    # Проверяем добавлен ли пользователь в бота по нику ----------------------------------------------------------------
    user = await UserApi.get_by_nickname(msg_data['nickname'])

    if user:
        final_text = text_user_exists
    else:
        final_text = text_end_add_user

        # Добавляем запись о регистрации в redis
        await redis_regs.set_new_registration(nickname=msg_data['nickname'][1:],
                                                    fullname=msg_data['fullname'],
                                                    profession=msg_data['profession'],
                                                    id_admin=message.from_user.id)

    await message.answer(text=final_text, parse_mode="html")
