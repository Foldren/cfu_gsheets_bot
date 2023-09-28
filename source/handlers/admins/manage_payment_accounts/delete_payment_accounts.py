from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.configurations.inline import cf_keyb_end_delete_org, cf_keyb_end_delete_partners, \
    cf_keyb_end_delete_payment_accounts
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.strings.inline import keyb_str_delete_partner, keyb_str_delete_payment_accounts
from components.texts.admins.manage_organizations import text_stop_delete_organizations
from components.texts.admins.manage_partners import text_start_delete_partners, text_end_delete_partners
from components.texts.admins.manage_payment_accounts import text_start_delete_payment_accounts, \
    text_end_delete_payment_accounts
from components.tools import get_callb_content, generate_zero_array, get_sure_delete_partner_msg, \
    get_sure_delete_payment_account_msg
from microservices.sql_models_extends.partner import PartnerExtend
from microservices.sql_models_extends.payment_account import PaymentAccountExtend
from states.admin.steps_manage_partners import StepsDeletePartners, StepsGetPartnersList
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
    list_button_names = []

    for p in payment_accounts:
        payment_account_org = await p.organization
        list_button_names.append(f'{payment_account_org.name}  -  {p.number}')

    status_list = await generate_zero_array(len(payment_accounts))
    list_index_payment_accounts = []

    # Генерируем список порядкового номера пунктов меню в клавиатуре
    for i in range(0, len(payment_accounts)):
        list_index_payment_accounts.append(i)

    keyboard_payment_accounts = await get_inline_keyb_markup(
        list_names=list_button_names,
        list_data=list_index_payment_accounts,
        callback_str="delete_choose_payment_accounts",
        number_cols=1,
    )

    # Сохраняем название выбранного пункта и лист статусов пунктов меню (выбран или нет)
    await state.set_data({
        'list_index_payment_accounts': list_index_payment_accounts,
        'status_list': status_list,
        'admin_payment_accounts': payment_accounts,
    })

    await callback.message.edit_text(
        text=text_start_delete_payment_accounts,
        reply_markup=keyboard_payment_accounts,
        parse_mode="html"
    )


@rt.callback_query(StepsDeletePaymentAccounts.start_delete_payment_accounts,
                   F.data.startswith("delete_choose_payment_accounts"))
async def change_delete_payment_accounts_list(callback: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()
    number_choose_payment_account = int(await get_callb_content(callback.data))
    new_data['status_list'][number_choose_payment_account] = 1 if new_data['status_list'][number_choose_payment_account] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': new_data['status_list'],
    })

    for i in range(0, len(new_data['admin_payment_accounts'])):
        status_emoji = '' if new_data['status_list'][i] == 0 else '☑️  '
        payment_account_org = await new_data["admin_payment_accounts"][i].organization
        new_name_btn = f'{status_emoji}' \
                       f'{payment_account_org.name} - {new_data["admin_payment_accounts"][i].number}'
        list_names.append(new_name_btn)

    keyboard_payment_accounts = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=new_data['list_index_payment_accounts'],
        callback_str="delete_choose_payment_accounts",
        number_cols=1,
        add_keyb_to_start=keyb_str_delete_payment_accounts
    )

    await callback.message.edit_text(
        text=text_start_delete_payment_accounts,
        reply_markup=keyboard_payment_accounts,
        parse_mode="html"
    )


# Предупреждающее сообщение --------------------------------------------------------------------------------------------
@rt.callback_query(StepsDeletePaymentAccounts.start_delete_payment_accounts,
                   F.data == "next_step_delete_payment_accounts")
async def sure_msg_delete_payment_accounts(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsDeletePaymentAccounts.sure_msg_delete_payment_accounts)
    state_data = await state.get_data()
    choose_payment_accounts_names = []

    for i in range(0, len(state_data['admin_payment_accounts'])):
        if state_data['status_list'][i] == 1:
            payment_account_org = await state_data['admin_payment_accounts'][i].organization
            choose_payment_accounts_names.append(payment_account_org.name + " - " + state_data['admin_payment_accounts'][i].number)

    sure_msg = await get_sure_delete_payment_account_msg(choose_payment_accounts_names)

    await callback.message.edit_text(text=sure_msg, reply_markup=cf_keyb_end_delete_payment_accounts, parse_mode="html")


@rt.callback_query(StepsDeletePaymentAccounts.sure_msg_delete_payment_accounts,
                   F.data == "cancel_delete_payment_accounts")
async def cancel_delete_payment_accounts(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=text_stop_delete_organizations, parse_mode="html")


@rt.callback_query(StepsDeletePaymentAccounts.sure_msg_delete_payment_accounts,
                   F.data == "end_delete_payment_accounts")
async def end_delete_payment_accounts(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()

    choose_payment_accounts_id_list = []

    for i in range(0, len(state_data['admin_payment_accounts'])):
        if state_data['status_list'][i] == 1:
            choose_payment_accounts_id_list.append(state_data['admin_payment_accounts'][i].id)

    await PaymentAccountExtend.delete_payment_accounts_by_ids(choose_payment_accounts_id_list)
    await callback.message.edit_text(text=text_end_delete_payment_accounts, parse_mode="html")
