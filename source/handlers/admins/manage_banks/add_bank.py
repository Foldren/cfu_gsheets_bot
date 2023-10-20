from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from cryptography.fernet import Fernet

from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.generators import get_inline_keyb_markup
from components.texts.admins.manage_banks import text_start_add_bank, text_select_bank_name, text_end_add_bank
from components.tools import get_msg_list_data, get_callb_content
from config import BANKS_RUS_NAMES, SECRET_KEY
from microservices.sql_models_extends.bank import BankExtend
from states.admin.steps_manage_banks import StepsGetBanksList, StepsAddBank

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetBanksList.get_list_banks, F.data.startswith("add_bank"))
async def start_add_bank(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsAddBank.start_add_bank)
    await callback.message.edit_text(text=text_start_add_bank, parse_mode="html")


@rt.message(StepsAddBank.start_add_bank)
async def select_bank_name(message: Message, state: FSMContext):
    await state.set_state(StepsAddBank.select_bank_name)

    data_new_partner = await get_msg_list_data(message.text)
    await state.set_data({
        'custom_name_new_bank': data_new_partner[0],
        'api_key_new_bank': Fernet(SECRET_KEY).encrypt(data_new_partner[1].encode()).decode('utf-8'),
    })

    keyboard = await get_inline_keyb_markup(
        list_names=list(BANKS_RUS_NAMES.values()),
        list_data=list(BANKS_RUS_NAMES.keys()),
        callback_str="selected_bank_name",
        number_cols=2,
    )

    await message.answer(text=text_select_bank_name, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsAddBank.select_bank_name, F.data.startswith("selected_bank_name"))
async def end_add_bank(callback: CallbackQuery, state: FSMContext):
    selected_bank_name = await get_callb_content(callback.data)
    st_data = await state.get_data()

    await BankExtend.add(
        custom_name=st_data['custom_name_new_bank'],
        bank_name=selected_bank_name,
        api_key=st_data['api_key_new_bank'].encode(),
        admin_id=callback.from_user.id,
    )

    await state.clear()
    await callback.message.edit_text(text=text_end_add_bank, parse_mode="html")


