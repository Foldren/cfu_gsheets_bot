from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.markups.inline import keyb_markup_end_delete_banks
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.inline_strings import keyb_str_delete_banks
from components.texts.admins.manage_banks import text_start_delete_banks, text_end_delete_banks
from components.texts.admins.manage_organizations import text_stop_delete_organizations
from components.tools import get_callb_content, generate_zero_array, get_sure_delete_banks_msg
from config import BANKS_RUS_NAMES
from microservices.sql_models_extends.bank import BankExtend
from states.admin.steps_manage_banks import StepsDeleteBanks, StepsGetBanksList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetBanksList.get_list_banks, F.data.startswith("delete_banks"))
async def start_delete_banks(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsDeleteBanks.start_delete_banks)

    banks = await BankExtend.get_admin_banks(callback.message.chat.id)

    status_list = await generate_zero_array(len(banks))
    list_index_banks = []

    # Генерируем список порядкового номера пунктов меню в клавиатуре
    for i in range(0, len(banks)):
        list_index_banks.append(i)

    keyboard_banks = await get_inline_keyb_markup(
        list_names=[f'{p["custom_name"]} - {BANKS_RUS_NAMES[p["bank_name"]]}' for p in banks],
        list_data=list_index_banks,
        callback_str="delete_choose_banks",
        number_cols=1,
    )

    # Сохраняем название выбранного пункта и лист статусов пунктов меню (выбран или нет)
    await state.set_data({
        'list_index_banks': list_index_banks,
        'status_list': status_list,
        'admin_banks': banks,
    })

    await callback.message.edit_text(
        text=text_start_delete_banks,
        reply_markup=keyboard_banks,
        parse_mode="html"
    )


@rt.callback_query(StepsDeleteBanks.start_delete_banks, F.data.startswith("delete_choose_banks"))
async def change_delete_banks_list(callback: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()

    number_choose_bank = int(await get_callb_content(callback.data))
    new_data['status_list'][number_choose_bank] = 1 if new_data['status_list'][number_choose_bank] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': new_data['status_list'],
    })

    for i in range(0, len(new_data['admin_banks'])):
        status_emoji = '' if new_data['status_list'][i] == 0 else '☑️'
        bank_rus_name = BANKS_RUS_NAMES[new_data["admin_banks"][i]["bank_name"]]
        new_name_btn = f'{status_emoji} {new_data["admin_banks"][i]["custom_name"]} - {bank_rus_name}'
        list_names.append(new_name_btn)

    keyboard_banks = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=new_data['list_index_banks'],
        callback_str="delete_choose_banks",
        number_cols=1,
        add_keyb_to_start=keyb_str_delete_banks
    )

    await callback.message.edit_text(
        text=text_start_delete_banks,
        reply_markup=keyboard_banks,
        parse_mode="html"
    )


# Предупреждающее сообщение --------------------------------------------------------------------------------------------
@rt.callback_query(StepsDeleteBanks.start_delete_banks, F.data == "next_step_delete_banks")
async def sure_msg_delete_banks(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsDeleteBanks.sure_msg_delete_banks)
    state_data = await state.get_data()
    choose_banks_names = []

    for i in range(0, len(state_data['admin_banks'])):
        if state_data['status_list'][i] == 1:
            choose_banks_names.append(state_data['admin_banks'][i]['custom_name'])

    sure_msg = await get_sure_delete_banks_msg(choose_banks_names)

    await callback.message.edit_text(text=sure_msg, reply_markup=keyb_markup_end_delete_banks, parse_mode="html")


@rt.callback_query(StepsDeleteBanks.sure_msg_delete_banks, F.data == "cancel_delete_banks")
async def cancel_delete_banks(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=text_stop_delete_organizations, parse_mode="html")


@rt.callback_query(StepsDeleteBanks.sure_msg_delete_banks, F.data == "end_delete_banks")
async def end_delete_banks(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()

    choose_banks_id_list = []

    for i in range(0, len(state_data['admin_banks'])):
        if state_data['status_list'][i] == 1:
            choose_banks_id_list.append(state_data['admin_banks'][i]['id'])

    await BankExtend.delete_banks_by_ids(choose_banks_id_list)
    await callback.message.edit_text(text=text_end_delete_banks, parse_mode="html")
