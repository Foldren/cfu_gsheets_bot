from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.markups.inline import keyb_markup_end_delete_partners
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.inline_strings import keyb_str_delete_partner
from components.texts.admins.manage_organizations import text_stop_delete_organizations
from components.texts.admins.manage_partners import text_start_delete_partners, text_end_delete_partners
from components.tools import get_callb_content, generate_zero_array, get_sure_delete_partner_msg
from microservices.sql_models_extends.partner import PartnerExtend
from states.admin.steps_manage_partners import StepsDeletePartners, StepsGetPartnersList

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetPartnersList.get_list_partners, F.data.startswith("delete_partners"))
async def start_delete_partners(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsDeletePartners.start_delete_partners)

    partners = await PartnerExtend.get_admin_partners(callback.message.chat.id)

    status_list = await generate_zero_array(len(partners))
    list_index_partners = []

    # Генерируем список порядкового номера пунктов меню в клавиатуре
    for i in range(0, len(partners)):
        list_index_partners.append(i)

    keyboard_partners = await get_inline_keyb_markup(
        list_names=[f'{p["name"]} - {p["inn"]}' for p in partners],
        list_data=list_index_partners,
        callback_str="delete_choose_partners",
        number_cols=1,
    )

    # Сохраняем название выбранного пункта и лист статусов пунктов меню (выбран или нет)
    await state.set_data({
        'list_index_partners': list_index_partners,
        'status_list': status_list,
        'admin_partners': partners,
    })

    await callback.message.edit_text(
        text=text_start_delete_partners,
        reply_markup=keyboard_partners,
        parse_mode="html"
    )


@rt.callback_query(StepsDeletePartners.start_delete_partners, F.data.startswith("delete_choose_partners"))
async def change_delete_partners_list(callback: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()

    number_choose_partner = int(await get_callb_content(callback.data))
    new_data['status_list'][number_choose_partner] = 1 if new_data['status_list'][number_choose_partner] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': new_data['status_list'],
    })

    for i in range(0, len(new_data['admin_partners'])):
        status_emoji = '' if new_data['status_list'][i] == 0 else '☑️'
        new_name_btn = f'{status_emoji} ' \
                       f'{new_data["admin_partners"][i]["name"]} - {new_data["admin_partners"][i]["inn"]}'
        list_names.append(new_name_btn)

    keyboard_partners = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=new_data['list_index_partners'],
        callback_str="delete_choose_partners",
        number_cols=1,
        add_keyb_to_start=keyb_str_delete_partner
    )

    await callback.message.edit_text(
        text=text_start_delete_partners,
        reply_markup=keyboard_partners,
        parse_mode="html"
    )


# Предупреждающее сообщение --------------------------------------------------------------------------------------------
@rt.callback_query(StepsDeletePartners.start_delete_partners, F.data == "next_step_delete_partner")
async def sure_msg_delete_partner(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsDeletePartners.sure_msg_delete_partners)
    state_data = await state.get_data()
    choose_partners_names = []

    for i in range(0, len(state_data['admin_partners'])):
        if state_data['status_list'][i] == 1:
            choose_partners_names.append(state_data['admin_partners'][i]['name'])

    sure_msg = await get_sure_delete_partner_msg(choose_partners_names)

    await callback.message.edit_text(text=sure_msg, reply_markup=keyb_markup_end_delete_partners, parse_mode="html")


@rt.callback_query(StepsDeletePartners.sure_msg_delete_partners, F.data == "cancel_delete_partners")
async def cancel_delete_partners(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=text_stop_delete_organizations, parse_mode="html")


@rt.callback_query(StepsDeletePartners.sure_msg_delete_partners, F.data == "end_delete_partners")
async def end_delete_partners(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()

    choose_partners_id_list = []

    for i in range(0, len(state_data['admin_partners'])):
        if state_data['status_list'][i] == 1:
            choose_partners_id_list.append(state_data['admin_partners'][i]['id'])

    await PartnerExtend.delete_partners_by_ids(choose_partners_id_list)
    await callback.message.edit_text(text=text_end_delete_partners, parse_mode="html")
