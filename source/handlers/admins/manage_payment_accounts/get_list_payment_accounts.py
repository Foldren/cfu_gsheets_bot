from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsAdminFilter
from components.keyboards_components.generators import get_inline_keyb_markup, get_keyb_str_manage_payment_accounts, \
    get_keyb_empty_list_payment_accounts
from components.texts.admins.manage_payment_accounts import text_get_list_payment_accounts
from components.tools import get_callb_content
from config import BANKS_RUS_NAMES
from microservices.sql_models_extends.bank import BankExtend
from microservices.sql_models_extends.payment_account import PaymentAccountExtend
from states.admin.steps_manage_banks import StepsGetBanksList
from states.admin.steps_manage_payment_accounts import StepsGetPaymentAccountsList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetBanksList.get_list_banks, F.data.startswith('get_bank_payment_accounts'))
async def get_payment_accounts_list(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsGetPaymentAccountsList.get_payment_accounts_list)

    selected_bank_id = await get_callb_content(callback.data)
    bank = await BankExtend.get_by_id(selected_bank_id)
    text_info_bank = f"<b>Расчётные счета</b>\n\n<u>Банк:</u> <b>{bank.custom_name}</b>\n" \
                     f"<u>Отделение:</u> <b>{BANKS_RUS_NAMES[bank.bank_name]}</b>\n\n"
    payment_accounts = await PaymentAccountExtend.get_bank_payment_accounts(selected_bank_id)

    if payment_accounts:
        list_button_names = []

        for p in payment_accounts:
            payment_account_org = await p.organization
            list_button_names.append(f'{payment_account_org.name}  -  {p.number}')

        keyboard = await get_inline_keyb_markup(
            list_names=list_button_names,
            callback_str="disabled_inline_btn",
            number_cols=1,
            add_keyb_to_start=await get_keyb_str_manage_payment_accounts(selected_bank_id)
        )
    else:
        keyboard = await get_keyb_empty_list_payment_accounts(selected_bank_id)

    await callback.message.edit_text(
        text=text_info_bank + text_get_list_payment_accounts,
        reply_markup=keyboard,
        parse_mode="html"
    )
