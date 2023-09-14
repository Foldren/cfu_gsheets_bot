from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router
from components.filters import IsUserFilter, IsRegistration
from components.keyboards import cf_keyb_start_user
from components.users.text_generators import get_text_fst_start_user, get_text_start_user
from services.models_extends.user import UserApi
from services.redis_extends.registrations import RedisRegistration
from services.redis_extends.user import RedisUser
from services.redis_extends.wallets import RedisUserWallets

rt = Router()


# Хэндлер на команду /start
@rt.message(Command(commands=["start"]), IsUserFilter())
async def start_user(message: Message, state: FSMContext):
    await state.clear()

    message_text = await get_text_fst_start_user(message.from_user.full_name)

    await message.answer(message_text, reply_markup=cf_keyb_start_user, parse_mode='html')


@rt.message(Command(commands=["start"]), IsRegistration())
async def register_user(message: Message, state: FSMContext,
                        redis_regs: RedisRegistration, redis_users: RedisUser, redis_wallets: RedisUserWallets):
    await state.clear()

    user_params = await redis_regs.get_registrations_params(message.from_user.username)

    # Удаляем регистрацию из redis
    await redis_regs.remove_registration(message.from_user.username)

    # Добавляем данные нового пользователя в бд sql
    await UserApi.add(
            chat_id=message.from_user.id,
            nickname="@" + user_params['nickname'],
            fullname=user_params['fullname'],
            profession=user_params['profession'],
            id_admin=user_params['id_admin']
        )

    # Добавляем кошелек
    await redis_wallets.set_new_wallets_list(message.from_user.id, ["Другой"])

    # Добавляем id в бд0 (для пользователей) redis
    await redis_users.add_new_user(message.from_user.id, int(user_params['id_admin']))

    message_text = await get_text_start_user(message.from_user.full_name)

    await message.answer(message_text, reply_markup=cf_keyb_start_user, parse_mode='html')
