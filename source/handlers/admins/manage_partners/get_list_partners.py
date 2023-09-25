from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsAdminFilter
from components.keyboards_components.configurations.inline import cf_keyb_get_empty_list_partners
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.strings.inline import keyb_str_get_full_list_partners
from components.texts.admins.manage_partners import text_get_list_partners
from services.sql_models_extends.partner import PartnerExtend
from states.admin.steps_manage_organizations import StepsGetOrganizationsList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter())
rt.callback_query.filter(IsAdminFilter())


@rt.message(F.text == "Контрагенты")
async def get_partners_list(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StepsGetOrganizationsList.get_list_organizations)

    partners = await PartnerExtend.get_admin_partners(message.from_user.id)

    if partners:
        keyboard = await get_inline_keyb_markup(
            list_names=[(p["name"] + ("  💤" if p["status"] == 0 else "")) for p in partners],
            list_data=[p["id"] for p in partners],
            callback_str="empty",
            number_cols=2,
            add_keyb_to_start=keyb_str_get_full_list_partners
        )
    else:
        keyboard = cf_keyb_get_empty_list_partners

    await message.answer(text=text_get_list_partners, reply_markup=keyboard, parse_mode="html")
