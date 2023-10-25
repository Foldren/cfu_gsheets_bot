from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router, F
from components.filters import IsAdminFilter
from components.keyboards_components.markups.inline import keyb_markup_empty_user_list
from components.keyboards_components.inline_strings import keyb_str_user_list
from components.texts.admins.manage_users import text_get_list_users
from components.keyboards_components.generators import get_inline_users_keyb_markup
from microservices.sql_models_extends.user import UserExtend
from states.admin.steps_manage_users import StepsGetListUsers

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


# Вывод списка пользователей из группы админа
@rt.message(F.text == "Сотрудники")
async def get_list_users(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StepsGetListUsers.get_list_users)

    users = await UserExtend.get_admin_users(message.from_user.id)

    if users:
        keyboard = await get_inline_users_keyb_markup(
            list_fullnames=[e["fullname"].split(" ")[1] + " - " + e["profession"] for e in users],
            list_names=[e["nickname"] for e in users],
            number_cols=2,
            add_keyb_to_start=keyb_str_user_list
        )
    else:
        keyboard = keyb_markup_empty_user_list

    await message.answer(text=text_get_list_users, reply_markup=keyboard, parse_mode="html")
