from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsAdminFilter
from components.keyboards_components.configurations.inline import cf_keyb_get_empty_list_partners
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.strings.inline import keyb_str_get_full_list_partners
from components.texts.admins.manage_partners import text_get_list_partners
from microservices.sql_models_extends.partner import PartnerExtend
from states.admin.steps_manage_partners import StepsGetPartnersList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Контрагенты")
async def get_partners_list(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StepsGetPartnersList.get_list_partners)

    partners = await PartnerExtend.get_admin_partners(message.from_user.id)

    if partners:
        keyboard = await get_inline_keyb_markup(
            list_names=[f'{p["name"]}  -  {p["inn"]}' for p in partners],
            callback_str="disabled_inline_btn",
            number_cols=1,
            add_keyb_to_start=keyb_str_get_full_list_partners
        )
    else:
        keyboard = cf_keyb_get_empty_list_partners

    await message.answer(text=text_get_list_partners, reply_markup=keyboard, parse_mode="html")
