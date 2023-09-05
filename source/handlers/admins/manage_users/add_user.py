from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F, Bot
from components.filters import IsAdminFilter
from components.texts import text_start_add_user, text_end_add_user, text_user_exists, text_get_id_user, \
    text_invalid_user_id
from components.tools import get_msg_user_data, set_memory_data, get_memory_data
from services.database_extends.user import UserApi
from states.steps_manage_users import StepsGetListUsers, StepsAddUser

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
async def get_id_user(message: Message, state: FSMContext, bot_object: Bot):
    await state.clear()
    await state.set_state(StepsAddUser.get_user_id)

    msg_data = await get_msg_user_data(message.text)

    await set_memory_data(bot_object, message, {
        'admin_id_new_u': message.from_user.id,
        'nickname_new_u': msg_data['nickname'],
        'fullname_new_u': msg_data['fullname'],
        'profession_new_u': msg_data['profession'],
    })

    await message.answer(text=text_get_id_user, parse_mode="html")


@rt.message(StepsAddUser.get_user_id)
async def end_add_user(message: Message, state: FSMContext, bot_object: Bot):
    await state.clear()

    # Проверка сообщения (forward или send) ----------------------------------------------------------------------------
    try:
        user_chat_id = message.forward_from.id
    except Exception:
        # Проверка id пользователя (если не число то все плохо)
        try:
            user_chat_id = int(message.text)
        except Exception:
            await message.answer(text=text_invalid_user_id, parse_mode="html")
            return

    # Проверяем добавлен ли пользователь в бота ------------------------------------------------------------------------
    user = await UserApi.get_by_id(user_chat_id)

    if user:
        final_text = text_user_exists
    else:
        final_text = text_end_add_user
        data_new_user = await get_memory_data(bot_object, message)
        await UserApi.add(
            chat_id=user_chat_id,
            nickname=data_new_user['nickname_new_u'],
            fullname=data_new_user['fullname_new_u'],
            profession=data_new_user['profession_new_u'],
            id_admin=data_new_user['admin_id_new_u']
        )

    await message.answer(text=final_text, parse_mode="html")
