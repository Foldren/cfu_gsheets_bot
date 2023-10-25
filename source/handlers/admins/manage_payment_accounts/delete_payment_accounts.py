from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.markups.inline import keyb_markup_end_delete_pa
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.inline_strings import keyb_str_delete_payment_accounts
from components.texts.admins.manage_organizations import text_stop_delete_organizations
from components.texts.admins.manage_payment_accounts import text_start_delete_payment_accounts, \
    text_end_delete_payment_accounts
from components.tools import get_callb_content, get_sure_delete_payment_account_msg, \
    get_changed_reply_keyb_with_checkbox, is_start_select_delete_btns, get_ids_delete_objects_from_keyb_callb
from microservices.sql_models_extends.payment_account import PaymentAccountExtend
from states.admin.steps_manage_payment_accounts import StepsDeletePaymentAccounts, StepsGetPaymentAccountsList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetPaymentAccountsList.get_payment_accounts_list, F.data.startswith("delete_payment_accounts"))
async def start_delete_payment_accounts(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsDeletePaymentAccounts.start_delete_payment_accounts)

    bank_id = await get_callb_content(callback.data)
    payment_accounts = await PaymentAccountExtend.get_bank_payment_accounts(bank_id)
    buttons_names = []
    buttons_callbacks = []

    for p in payment_accounts:
        payment_account_org = await p.organization
        buttons_names.append(f'{payment_account_org.name} - {p.number}')
        buttons_callbacks.append(p.id)

    keyboard_markup = await get_inline_keyb_markup(
        list_names=buttons_names,
        list_data=buttons_callbacks,
        callback_str=f"select_delete_pa",
        number_cols=1
    )

    await callback.message.edit_text(
        text=text_start_delete_payment_accounts,
        reply_markup=keyboard_markup,
        parse_mode="html"
    )


@rt.callback_query(StepsDeletePaymentAccounts.start_delete_payment_accounts, F.data.startswith("select_delete_pa"))
async def change_delete_payment_accounts_list(callback: CallbackQuery, state: FSMContext):
    keyboard_markup = await get_changed_reply_keyb_with_checkbox(callback, 'checkbox_minimum_one', ['⏩'])
    start_delete_flag = await is_start_select_delete_btns(state)

    if start_delete_flag:
        keyboard_markup.inline_keyboard.insert(0, keyb_str_delete_payment_accounts)

    await callback.message.edit_text(
        text=text_start_delete_payment_accounts,
        reply_markup=keyboard_markup,
        parse_mode="html"
    )


# Предупреждающее сообщение --------------------------------------------------------------------------------------------
@rt.callback_query(StepsDeletePaymentAccounts.start_delete_payment_accounts, F.data == "next_step_delete_pa")
async def sure_msg_delete_payment_accounts(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsDeletePaymentAccounts.sure_msg_delete_payment_accounts)

    ids_delete_pa = await get_ids_delete_objects_from_keyb_callb(callback, '☑️')
    await state.set_data({'ids_delete_pa': ids_delete_pa})
    payment_accounts = await PaymentAccountExtend.get_pa_by_ids(ids_delete_pa)
    choose_payment_accounts_names = []

    for p in payment_accounts:
        payment_account_org = await p.organization
        choose_payment_accounts_names.append(payment_account_org.name + " - " + p.number)

    sure_msg = await get_sure_delete_payment_account_msg(choose_payment_accounts_names)

    await callback.message.edit_text(text=sure_msg, reply_markup=keyb_markup_end_delete_pa, parse_mode="html")


@rt.callback_query(StepsDeletePaymentAccounts.sure_msg_delete_payment_accounts,
                   F.data == "cancel_delete_payment_accounts")
async def cancel_delete_payment_accounts(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=text_stop_delete_organizations, parse_mode="html")


@rt.callback_query(StepsDeletePaymentAccounts.sure_msg_delete_payment_accounts,
                   F.data == "end_delete_payment_accounts")
async def end_delete_payment_accounts(callback: CallbackQuery, state: FSMContext):
    st_data = await state.get_data()

    await PaymentAccountExtend.delete_payment_accounts_by_ids(st_data['ids_delete_pa'])
    await state.clear()
    await callback.message.edit_text(text=text_end_delete_payment_accounts, parse_mode="html")
