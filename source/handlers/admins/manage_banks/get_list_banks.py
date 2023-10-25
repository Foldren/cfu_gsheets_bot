from typing import Union
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsAdminFilter
from components.keyboards_components.markups.inline import keyb_markup_get_empty_list_banks
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.inline_strings import keyb_str_get_full_list_banks
from components.texts.admins.manage_banks import text_get_list_banks
from components.tools import answer_or_edit_message
from config import BANKS_RUS_NAMES
from microservices.sql_models_extends.bank import BankExtend
from states.admin.steps_manage_banks import StepsGetBanksList
from states.admin.steps_manage_payment_accounts import StepsGetPaymentAccountsList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Банки и расчётные счета")
@rt.callback_query(StepsGetPaymentAccountsList.get_payment_accounts_list, F.data.startswith('back_to_banks'))
async def get_banks_list(callb_or_msg: Union[Message, CallbackQuery], state: FSMContext):
    await state.clear()
    await state.set_state(StepsGetBanksList.get_list_banks)

    message = callb_or_msg.message if hasattr(callb_or_msg, "data") else callb_or_msg
    banks = await BankExtend.get_admin_banks(message.chat.id)
    list_btn_names = []

    for b in banks:
        list_btn_names.append(f'{b["custom_name"]}  -  {BANKS_RUS_NAMES[b["bank_name"]]}')

    if banks:
        keyboard = await get_inline_keyb_markup(
            list_names=list_btn_names,
            list_data=[b["id"] for b in banks],
            callback_str="get_bank_payment_accounts",
            number_cols=1,
            add_keyb_to_start=keyb_str_get_full_list_banks
        )
    else:
        keyboard = keyb_markup_get_empty_list_banks

    await answer_or_edit_message(
        message=message,
        flag_answer=not hasattr(callb_or_msg, "data"),
        text=text_get_list_banks,
        keyboard_markup=keyboard,
    )