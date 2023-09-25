from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.texts.admins.manage_partners import text_start_add_partner, text_end_add_partner
from components.tools import get_msg_list_data
from services.sql_models_extends.partner import PartnerExtend
from states.admin.steps_manage_partners import StepsGetPartnersList, StepsAddPartner

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetPartnersList.get_list_partners, F.data.startswith("add_partner"))
async def start_add_partner(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsAddPartner.start_add_partner)
    await callback.message.edit_text(text=text_start_add_partner, parse_mode="html")


@rt.message(StepsAddPartner.start_add_partner)
async def end_add_partner(message: Message, state: FSMContext):
    data_new_partner = await get_msg_list_data(message.text)

    await PartnerExtend.add(
        inn=data_new_partner[0],
        name=data_new_partner[1],
        admin_id=message.from_user.id,
    )

    await state.clear()
    await message.answer(text=text_end_add_partner, parse_mode="html")


