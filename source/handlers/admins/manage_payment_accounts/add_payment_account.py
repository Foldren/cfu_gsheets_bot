from datetime import datetime
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.generators import get_inline_keyb_markup
from components.texts.admins.manage_payment_accounts import text_start_add_payment_account, \
    text_select_payment_account_organization, text_end_add_payment_account, text_wrong_datetime
from components.tools import get_msg_list_data, get_callb_content
from microservices.sql_models_extends.organization import OrganizationExtend
from microservices.sql_models_extends.payment_account import PaymentAccountExtend
from states.admin.steps_manage_payment_accounts import StepsGetPaymentAccountsList, StepsAddPaymentAccount

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetPaymentAccountsList.get_payment_accounts_list, F.data.startswith("add_payment_account"))
async def start_add_payment_account(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await get_callb_content(callback.data)
    await state.set_data({'bank_id': await get_callb_content(callback.data)})
    await state.set_state(StepsAddPaymentAccount.start_add_payment_account)
    await callback.message.edit_text(text=text_start_add_payment_account, parse_mode="html")


@rt.message(StepsAddPaymentAccount.start_add_payment_account)
async def select_payment_account_organization(message: Message, state: FSMContext):
    await state.set_state(StepsAddPaymentAccount.select_payment_account_organization)

    msg_data = await get_msg_list_data(message.text)

    try:
        selected_date_load = datetime.strptime(msg_data[1], "%Y-%m-%d")
        if selected_date_load.year != datetime.now().year:
            raise Exception("Пользователь неправильно задал дату стартовой отгрузки")
    except Exception:
        await message.answer(text=text_wrong_datetime, parse_mode="html")
        return

    await state.update_data({
        'number_new_payment_account': msg_data[0],
        'first_date_load_statement': msg_data[1],
    })

    admin_organizations = await OrganizationExtend.get_admin_organizations(message.from_user.id)

    keyboard = await get_inline_keyb_markup(
        list_names=[o['name'] for o in admin_organizations],
        list_data=[o['id'] for o in admin_organizations],
        callback_str="selected_payment_account_organization",
        number_cols=2,
    )

    await message.answer(text=text_select_payment_account_organization, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsAddPaymentAccount.select_payment_account_organization,
                   F.data.startswith("selected_payment_account_organization"))
async def end_add_payment_account(callback: CallbackQuery, state: FSMContext):
    selected_organization_pa_id = await get_callb_content(callback.data)
    st_data = await state.get_data()

    await PaymentAccountExtend.add(
        number=st_data['number_new_payment_account'],
        first_date_load_statement=st_data['first_date_load_statement'],
        bank_id=st_data['bank_id'],
        organization_id=selected_organization_pa_id,
    )

    await state.clear()
    await callback.message.edit_text(text=text_end_add_payment_account, parse_mode="html")


