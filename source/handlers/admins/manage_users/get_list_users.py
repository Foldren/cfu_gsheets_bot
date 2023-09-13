from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram import Router, F
from components.filters import IsAdminFilter
from components.keyboards import cf_keyb_empty_user_list, keyb_str_user_list
from components.admins.texts import text_get_list_users
from components.tools import get_inline_users_keyb_markup
from services.models_extends.user import UserApi
from states.admin.steps_manage_users import StepsGetListUsers

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


# Вывод списка пользователей из группы админа
@rt.message(F.text == "Сотрудники")
async def get_list_users(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StepsGetListUsers.get_list_users)

    users = await UserApi.get_admin_users(message.from_user.id)

    if users:
        keyboard = await get_inline_users_keyb_markup(
            list_fullnames=[e["fullname"].split(" ")[1] + " - " + e["profession"] for e in users],
            list_names=[e["nickname"] for e in users],
            number_cols=2,
            add_keyb_to_start=keyb_str_user_list
        )
    else:
        keyboard = cf_keyb_empty_user_list

    await message.answer(text=text_get_list_users, reply_markup=keyboard, parse_mode="html")
