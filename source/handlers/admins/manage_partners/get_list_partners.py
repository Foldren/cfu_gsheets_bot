from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsAdminFilter
from components.keyboards_components.markups.inline import keyb_markup_get_empty_list_partners
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.inline_strings import keyb_str_get_full_list_partners
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

    partners = await PartnerExtend.get_admin_partners(message.chat.id)
    list_names = []
    list_callbacks = []

    for p in partners:
        if p['bank_reload_category__id']:
            list_names.append(f'{p["name"]}  -  {p["inn"]}')
            list_callbacks.append('disabled_inline_btn')
        else:
            list_names.append(f'📥 {p["name"]}  -  {p["inn"]}')
            list_callbacks.append(f'distribute_auto_load_partner:{p["id"]}')

    if partners:
        keyboard = await get_inline_keyb_markup(
            list_names=list_names,
            list_data=list_callbacks,
            callback_str="",
            number_cols=1,
            add_keyb_to_start=keyb_str_get_full_list_partners
        )
    else:
        keyboard = keyb_markup_get_empty_list_partners

    await message.answer(text=text_get_list_partners, reply_markup=keyboard, parse_mode="html")


