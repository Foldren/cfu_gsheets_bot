from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery
from components.filters import IsAdminFilter, IsNotMainMenuMessage
from components.keyboards_components.markups.inline import keyb_markup_end_delete_org
from components.keyboards_components.generators import get_inline_keyb_markup
from components.keyboards_components.inline_strings import keyb_str_delete_org
from components.texts.admins.manage_organizations import text_start_delete_organizations, \
    text_stop_delete_organizations, text_end_delete_organizations
from components.tools import get_callb_content, generate_zero_array, get_sure_delete_org_msg
from microservices.sql_models_extends.organization import OrganizationExtend
from states.admin.steps_manage_organizations import StepsGetOrganizationsList, StepsDeleteOrganizations

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.callback_query(StepsGetOrganizationsList.get_list_organizations, F.data.startswith("delete_organizations"))
async def start_delete_organizations(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await state.set_state(StepsDeleteOrganizations.start_delete_organizations)

    organizations = await OrganizationExtend.get_admin_organizations(callback.message.chat.id)

    status_list = await generate_zero_array(len(organizations))
    list_index_organizations = []
    list_buttons_name = []

    # Генерируем список порядкового номера пунктов меню в клавиатуре
    for i in range(0, len(organizations)):
        list_index_organizations.append(i)

    # Генерируем список наименований кнопок с пунктами меню
    for e in organizations:
        status_organization = "  💤" if e["status"] == 0 else ""
        list_buttons_name.append(e["name"] + " " + status_organization)

    keyboard_organizations = await get_inline_keyb_markup(
        list_names=list_buttons_name,
        list_data=list_index_organizations,
        callback_str="delete_choose_organizations",
        number_cols=2,
    )

    # Сохраняем название выбранного пункта и лист статусов пунктов меню (выбран или нет)
    await state.set_data({
        'list_index_organizations': list_index_organizations,
        'status_list': status_list,
        'admin_organizations': organizations,
    })

    await callback.message.edit_text(
        text=text_start_delete_organizations,
        reply_markup=keyboard_organizations,
        parse_mode="html"
    )


@rt.callback_query(StepsDeleteOrganizations.start_delete_organizations,
                   F.data.startswith("delete_choose_organizations"))
async def change_delete_organizations_list(callback: CallbackQuery, state: FSMContext):
    new_data = await state.get_data()

    number_choose_organization = int(await get_callb_content(callback.data))
    new_data['status_list'][number_choose_organization] = 1 if new_data['status_list'][
                                                                   number_choose_organization] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': new_data['status_list'],
    })

    for i in range(0, len(new_data['admin_organizations'])):
        status_emoji = '' if new_data['status_list'][i] == 0 else '☑️'
        status_organization = "  💤" if new_data["admin_organizations"][i]["status"] == 0 else ""
        new_name_btn = " ".join([status_emoji, new_data["admin_organizations"][i]["name"], status_organization])
        list_names.append(new_name_btn)

    keyboard_organizations = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=new_data['list_index_organizations'],
        callback_str="delete_choose_organizations",
        number_cols=2,
        add_keyb_to_start=keyb_str_delete_org
    )

    await callback.message.edit_text(
        text=text_start_delete_organizations,
        reply_markup=keyboard_organizations,
        parse_mode="html"
    )


# Предупреждающее сообщение --------------------------------------------------------------------------------------------
@rt.callback_query(StepsDeleteOrganizations.start_delete_organizations, F.data == "next_step_delete_organization")
async def sure_msg_delete_organization(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsDeleteOrganizations.sure_msg_delete_organizations)
    state_data = await state.get_data()
    choose_organizations_names = []

    for i in range(0, len(state_data['admin_organizations'])):
        if state_data['status_list'][i] == 1:
            choose_organizations_names.append(state_data['admin_organizations'][i]['name'])

    sure_msg = await get_sure_delete_org_msg(choose_organizations_names)

    await callback.message.edit_text(text=sure_msg, reply_markup=keyb_markup_end_delete_org, parse_mode="html")


@rt.callback_query(StepsDeleteOrganizations.sure_msg_delete_organizations, F.data == "cancel_delete_organizations")
async def cancel_delete_organizations(callback: CallbackQuery, state: FSMContext):
    await state.clear()
    await callback.message.edit_text(text=text_stop_delete_organizations, parse_mode="html")


@rt.callback_query(StepsDeleteOrganizations.sure_msg_delete_organizations, F.data == "end_delete_organizations")
async def end_delete_organizations(callback: CallbackQuery, state: FSMContext):
    state_data = await state.get_data()
    await state.clear()

    choose_organizations_id_list = []

    for i in range(0, len(state_data['admin_organizations'])):
        if state_data['status_list'][i] == 1:
            choose_organizations_id_list.append(state_data['admin_organizations'][i]['id'])

    await OrganizationExtend.delete_organizations_by_ids(choose_organizations_id_list)

    await callback.message.edit_text(text=text_end_delete_organizations, parse_mode="html")
