from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from aiogram import Router, F, Bot
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.texts.admins.manage_users import text_get_id_user, text_invalid_user_id, text_start_change_user, \
    text_change_user, text_end_change_user, text_end_change_id_user
from components.tools import get_callb_content, get_msg_user_data, set_memory_data, get_memory_data
from components.keyboards_components.generators import get_inline_users_keyb_markup, get_inline_keyb_change_user
from microservices.sql_models_extends.user import UserExtend
from states.admin.steps_manage_users import StepsGetListUsers, StepsChangeUser

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetListUsers.get_list_users, F.data == "change_user")
async def start_change_user(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsChangeUser.start_change_user)

    users = await UserExtend.get_admin_users(callback.message.chat.id)

    keyboard = await get_inline_users_keyb_markup(
        list_fullnames=[e["fullname"].split(" ")[1] + " - " + e["profession"] for e in users],
        list_names=[e["chat_id"] for e in users],
        number_cols=2,
        callb="change_this_user",
        url=False
    )

    await callback.message.edit_text(text=text_start_change_user, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsChangeUser.start_change_user, F.data.startswith("change_this_user"))
async def set_new_data_user(callback: CallbackQuery, state: FSMContext, bot_object: Bot):
    await state.clear()
    await state.set_state(StepsChangeUser.choose_new_data_user)

    id_user = await get_callb_content(callback.data)
    user = await UserExtend.get_by_id(id_user)

    msg_text = f"<b>Редактирование сотрудника:</b> (шаг 2)\n\n" \
               f"<u>Chat_id:</u> <b>{user.chat_id}</b>\n" \
               f"<u>Полное имя:</u> <b>{user.fullname}</b>\n\n"
    example_text = f"<code>{user.nickname}\n{user.fullname}\n{user.profession}</code>"

    await set_memory_data(bot_object, callback.message, {
        'id_change_u': user.chat_id
    })

    await callback.message.edit_text(text=msg_text + text_change_user + example_text, parse_mode="html")


@rt.message(StepsChangeUser.choose_new_data_user)
async def end_set_new_main_data_user(message: Message, state: FSMContext, bot_object: Bot):
    msg_data = await get_msg_user_data(message.text)
    memory_data = await get_memory_data(bot_object, message)

    await UserExtend.update_by_id(
        chat_id=memory_data['id_change_u'],
        nickname=msg_data['nickname'],
        fullname=msg_data['fullname'],
        profession=msg_data['profession'],
        id_admin=message.from_user.id
    )

    await state.clear()
    await message.answer(text=text_end_change_user, parse_mode="html")


