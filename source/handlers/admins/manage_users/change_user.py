from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F, Bot
from components.filters import IsAdminFilter
from components.admins.texts import text_start_change_user, text_change_user, text_end_change_user, text_get_id_user, \
    text_invalid_user_id, text_end_change_id_user
from components.tools import get_inline_users_keyb_markup, get_callb_content, get_inline_keyb_change_user, \
    get_msg_user_data, set_memory_data, get_memory_data
from services.models_extends.user import UserApi
from states.steps_manage_users import StepsGetListUsers, StepsChangeUser

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


@rt.callback_query(StepsGetListUsers.get_list_users, F.data == "change_user")
async def start_change_user(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsChangeUser.start_change_user)

    users = await UserApi.get_admin_users(callback.message.chat.id)

    keyboard = await get_inline_users_keyb_markup(
        list_fullnames=[e["fullname"].split(" ")[1] + " - " + e["profession"] for e in users],
        list_names=[e["chat_id"] for e in users],
        number_cols=2,
        callb="change_this_user",
        url=False
    )

    await callback.message.edit_text(text=text_start_change_user, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsChangeUser.start_change_user, F.data.startswith("change_this_user"))
async def choose_new_data_user(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsChangeUser.choose_new_data_user)

    id_user = await get_callb_content(callback.data)
    user = await UserApi.get_by_id(id_user)

    msg_text = f"<b>Chat_id</b> - {user.chat_id}\n" \
               f"<b>Полное имя</b> - {user.fullname}\n" \
               f"<b>Никнейм</b> - {user.nickname}\n" \
               f"<b>Профессия</b> - {user.profession}"

    await callback.message.edit_text(
        text=msg_text,
        reply_markup=await get_inline_keyb_change_user(id_user),
        parse_mode="html")


# Изменение основных данных --------------------------------------------------------------------------------------------
@rt.callback_query(StepsChangeUser.choose_new_data_user, F.data.startswith("change_data_user"))
async def set_new_main_data_user(callback: CallbackQuery, state: FSMContext, bot_object: Bot):
    await state.clear()
    await state.set_state(StepsChangeUser.set_new_main_data_user)

    id_user = await get_callb_content(callback.data)
    user = await UserApi.get_by_id(id_user)

    msg_text = f"<u>Пользователь:</u> {user.nickname}\n<b>{user.fullname}</b> - {user.profession} \n\n"
    example_text = f"<code>{user.nickname}\n{user.fullname}\n{user.profession}</code>"

    await set_memory_data(bot_object, callback.message, {
        'id_change_u': user.chat_id
    })

    await callback.message.edit_text(text=msg_text + text_change_user + example_text, parse_mode="html")


@rt.message(StepsChangeUser.set_new_main_data_user)
async def end_set_new_main_data_user(message: Message, state: FSMContext, bot_object: Bot):
    msg_data = await get_msg_user_data(message.text)
    memory_data = await get_memory_data(bot_object, message)

    await UserApi.update_by_id(
        chat_id=memory_data['id_change_u'],
        nickname=msg_data['nickname'],
        fullname=msg_data['fullname'],
        profession=msg_data['profession'],
        id_admin=message.from_user.id
    )

    await state.clear()
    await message.answer(text=text_end_change_user, parse_mode="html")


# Изменение id ---------------------------------------------------------------------------------------------------------
@rt.callback_query(StepsChangeUser.choose_new_data_user, F.data.startswith("change_id_user"))
async def change_id_user(callback: CallbackQuery, state: FSMContext, bot_object: Bot):
    await state.clear()
    await state.set_state(StepsChangeUser.set_new_id_user)

    id_user = await get_callb_content(callback.data)
    user = await UserApi.get_by_id(id_user)

    msg_text = f"<code>Пользователь:</code> <b>{user.fullname}</b> - {user.profession} ({user.nickname})\n\n"

    await set_memory_data(bot_object, callback.message, {
        'id_change_u': id_user
    })

    await callback.message.edit_text(text=msg_text + text_get_id_user, parse_mode="html")


@rt.message(StepsChangeUser.set_new_id_user)
async def end_add_user(message: Message, state: FSMContext, bot_object: Bot):
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

    data_user = await get_memory_data(bot_object, message)

    await UserApi.update_by_id(
        chat_id=data_user['id_change_u'],
        new_chat_id=user_chat_id
    )

    await state.clear()
    await message.answer(text=text_end_change_id_user, parse_mode="html")



