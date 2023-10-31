from aiogram.filters import Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, BotCommandScopeAllPrivateChats
from aiogram import Router, Bot, F
from components.commands import main_commands
from components.filters import IsUserFilter, IsRegistration
from components.keyboards_components.generators import get_reply_keyb_markup_start
from components.keyboards_components.markups.reply import keyb_markup_start_user
from components.text_generators.users import get_text_fst_start_user, get_text_start_user
from microservices.sql_models_extends.user import UserExtend
from microservices.redis_models.registrations import RedisRegistration
from microservices.redis_models.user import RedisUser
from microservices.redis_models.wallets import RedisUserWallets

rt = Router()


# Хэндлер на команду /start
@rt.message(Command(commands=["start", "restart"]), IsUserFilter(), F.chat.type == "private")
async def start_user(message: Message, state: FSMContext, bot_object: Bot):
    await state.clear()

    message_text = await get_text_fst_start_user(message.from_user.full_name)

    await bot_object.set_my_commands(commands=main_commands, scope=BotCommandScopeAllPrivateChats())
    await message.answer(message_text, reply_markup=await get_reply_keyb_markup_start(message.from_user.id, "user"), parse_mode='html')


@rt.message(Command(commands=["start"]), IsRegistration(), F.chat.type == "private")
async def register_user(message: Message, state: FSMContext,
                        redis_regs: RedisRegistration, redis_users: RedisUser, redis_wallets: RedisUserWallets):
    await state.clear()

    user_params = await redis_regs.get_registrations_params(message.from_user.username)

    # Удаляем регистрацию из redis
    await redis_regs.remove_registration(message.from_user.username)

    # Добавляем данные нового пользователя в бд sql
    await UserExtend.add(
            chat_id=int(message.from_user.id),
            nickname="@" + user_params['nickname'],
            fullname=user_params['fullname'],
            profession=user_params['profession'],
            id_admin=int(user_params['id_admin']),
            bet=int(user_params['bet']),
            increased_bet=int(user_params['increased_bet']),
        )

    # Добавляем кошелек
    await redis_wallets.set_new_wallets_list(message.from_user.id, ["Другой"])

    # Добавляем id в бд0 (для пользователей) redis
    await redis_users.add_new_user(
        user_id=message.from_user.id,
        category='user',
        admin_id=int(user_params['id_admin'])
    )

    message_text = await get_text_start_user(message.from_user.full_name)

    await message.answer(message_text, reply_markup=await get_reply_keyb_markup_start(message.from_user.id, "user"), parse_mode='html')
