import traceback

from aiofiles.os import mkdir
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aioshutil import copy
from components.filters import IsSuperAdminFilter, IsNotMainMenuMessage
from components.texts.super_admin.add_new_client import text_start_add_client, text_success_add_client, \
    text_success_error_add_client
from components.tools import get_msg_list_data
from config import CHECKS_PATH, IMAGES_PATH
from microservices.redis_models.user import RedisUser
from microservices.redis_models.wallets import RedisUserWallets
from microservices.sql_models_extends.user import UserExtend
from states.super_admin.steps_add_new_client import StepsAddNewClient

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsSuperAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsSuperAdminFilter(), F.message.chat.type == "private")


@rt.message(F.text == '⭐️ Добавить нового клиента ⭐️')
async def start_add_new_client(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StepsAddNewClient.start_add_new_client)
    await message.answer(text=text_start_add_client)


@rt.message(StepsAddNewClient.start_add_new_client, IsNotMainMenuMessage())
async def end_add_new_client(message: Message, state: FSMContext, redis_users: RedisUser, redis_wallets: RedisUserWallets):
    """
    Хэндлер на добавление нового клиента, параметры месседжа в следующем порядке
    chat_id, никнейм, полное имя, ссылка на папку для чеков, ссылка на таблицу

    :param redis_users: объект redis db с users
    :param message: объект с данными нового клиента
    :param state: стейт начала добавления
    """

    msg_data = await get_msg_list_data(message.text)

    await state.clear()
    try:
        await UserExtend.add(
            chat_id=int(msg_data[0]),
            nickname=msg_data[1],
            fullname=msg_data[2],
            profession="администратор",
            bet=0,
            increased_bet=0,
            google_table_url=msg_data[3],
            google_drive_dir_url=msg_data[4]
        )

        await mkdir(CHECKS_PATH + msg_data[0])
        await copy(IMAGES_PATH + 'fstfile.jpg', CHECKS_PATH + msg_data[0] + '/fstfile.jpg')

        await redis_wallets.set_new_wallets_list(msg_data[0], ["Другой"])
        await redis_users.add_new_user(msg_data[0], 'admin')

        await message.answer(text=text_success_add_client)

    except Exception:
        traceback.print_exc()
        await message.answer(text=text_success_error_add_client)

