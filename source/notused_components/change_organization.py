# from aiogram import Router, F
# from aiogram.fsm.context import FSMContext
# from aiogram.types import CallbackQuery, Message
# from components.filters import IsAdminFilter, IsNotMainMenuMessage
# from components.keyboards_components.generators import get_inline_keyb_markup, get_inline_keyb_change_organization
# from components.keyboards_components.strings.inline import keyb_str_change_observers_org
# from components.texts.admins.manage_organizations import text_choose_param_to_change_organization, \
#     text_change_name_organization, text_end_change_organization, text_choose_observers_organization, \
#     text_end_change_observers_organization
# from components.tools import get_callb_content, generate_observers_list, get_msg_list_data
# from services.sql_models_extends.organization import OrganizationExtend
# from states.admin.steps_manage_organizations import StepsGetOrganizationsList, StepsChangeOrganization
#
# rt = Router()
#
# # Фильтр на проверку категории доступа пользователя
# rt.message.filter(IsAdminFilter(), IsNotMainMenuMessage())
# rt.callback_query.filter(IsAdminFilter())
#
#
# @rt.callback_query(StepsGetOrganizationsList.get_list_organizations, F.data.startswith("change_organization"))
# @rt.callback_query(StepsChangeOrganization.start_change_organization, F.data.startswith("change_status_organization"))
# async def choose_menu_item_params_to_change(callback: CallbackQuery, state: FSMContext):
#     await state.clear()
#     await state.set_state(StepsChangeOrganization.start_change_organization)
#
#     id_organization = await get_callb_content(callback.data)
#     organization = await OrganizationExtend.get_by_id(id_organization)
#
#     await state.update_data({
#         'id_organization': id_organization,
#     })
#
#     if "change_status_organization" in callback.data:
#         await OrganizationExtend.invert_status(organization)
#
#     final_text = f"<u>Выбрано юр. лицо</u>: <b>{organization.name}</b>\n" + text_choose_param_to_change_organization
#     keyboard = await get_inline_keyb_change_organization(id=organization.id, status=organization.status)
#
#     await callback.message.edit_text(text=final_text, reply_markup=keyboard, parse_mode="html")
#
#
# @rt.callback_query(StepsChangeOrganization.start_change_organization, F.data.startswith("change_params_organization"))
# async def start_change_params_organization(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(StepsChangeOrganization.change_params_organization)
#     st_data = await state.get_data()
#     organization = await OrganizationExtend.get_by_id(st_data['id_organization'])
#     txt_msg = text_change_name_organization + f"<b>Пример:</b>\n<code>{organization.inn}\n{organization.name}</code>"
#
#     await callback.message.edit_text(text=txt_msg, parse_mode="html")
#
#
# @rt.message(StepsChangeOrganization.change_params_organization)
# async def end_change_params_organization(message: Message, state: FSMContext):
#     state_data = await state.get_data()
#     msg_data = await get_msg_list_data(message.text)
#
#     await state.clear()
#     await OrganizationExtend.update_by_id(
#         organization_id=state_data['id_organization'],
#         inn=msg_data[0],
#         name=msg_data[1],
#     )
#     await message.answer(text=text_end_change_organization, parse_mode="html")
#
#
# # Изменение списка наблюдателей ----------------------------------------------------------------------------------------
# @rt.callback_query(StepsChangeOrganization.start_change_organization,
#                    F.data.startswith("start_change_observers_organization"))
# async def start_change_observers_organization(callback: CallbackQuery, state: FSMContext):
#     await state.set_state(StepsChangeOrganization.change_observers_organization)
#
#     organization_id = await get_callb_content(callback.data)
#     users_and_obs = await OrganizationExtend.get_admin_users_with_flag_observer(admin_id=callback.message.chat.id,
#                                                                                 organization_id=organization_id)
#     status_list = await generate_observers_list(users_and_obs)
#     list_index_users = []
#     list_buttons_name = []
#
#     # Генерируем список порядкового номера пользователей в клавиатуре
#     for i in range(0, len(users_and_obs)):
#         list_index_users.append(i)
#
#     # Генерируем список наименований кнопок с пользователями
#     for e in users_and_obs:
#         status_emoji = "☑️" if e["observer"] else ""
#         list_buttons_name.append(f'{status_emoji} {e["fullname"].split(" ")[1]} - {e["profession"]}')
#
#     keyboard_users = await get_inline_keyb_markup(
#         list_names=list_buttons_name,
#         list_data=list_index_users,
#         callback_str="change_observers_organization",
#         number_cols=2,
#         add_keyb_to_start=keyb_str_change_observers_org
#     )
#
#     # Сохраняем название выбранного пункта и лист статусов пользователей (выбран или нет)
#     await state.update_data({
#         'list_index_users': list_index_users,
#         'status_list': status_list,
#         'users_and_obs': users_and_obs,
#     })
#
#     await callback.message.edit_text(
#         text=text_choose_observers_organization,
#         reply_markup=keyboard_users,
#         parse_mode="html"
#     )
#
#
# @rt.callback_query(StepsChangeOrganization.change_observers_organization, F.data.startswith("change_observers_organization"))
# async def change_observers_organization(callback: CallbackQuery, state: FSMContext):
#     data_state = await state.get_data()
#     number_choose_user = int(await get_callb_content(callback.data))
#     data_state['status_list'][number_choose_user] = 1 if data_state['status_list'][number_choose_user] == 0 else 0
#     list_names = []
#
#     await state.update_data({
#         'status_list': data_state['status_list'],
#     })
#
#     for i in range(0, len(data_state['users_and_obs'])):
#         status_emoji = '' if data_state['status_list'][i] == 0 else '☑️'
#         list_names.append(
#             f'{status_emoji} {data_state["users_and_obs"][i]["fullname"].split(" ")[1]} - {data_state["users_and_obs"][i]["profession"]}')
#
#     keyboard_users = await get_inline_keyb_markup(
#         list_names=list_names,
#         list_data=data_state['list_index_users'],
#         callback_str="change_observers_menu_item",
#         number_cols=2,
#         add_keyb_to_start=keyb_str_change_observers_org
#     )
#
#     await callback.message.edit_text(
#         text=text_choose_observers_organization,
#         reply_markup=keyboard_users,
#         parse_mode="html"
#     )
#
#
# @rt.callback_query(StepsChangeOrganization.change_observers_organization, F.data == "save_change_obs_organization")
# async def end_change_observers_organization(callback: CallbackQuery, state: FSMContext):
#     data_state = await state.get_data()
#     await state.clear()
#
#     list_id_users = []
#
#     # Генерируем список выбранных пользователей
#     for i in range(0, len(data_state['users_and_obs'])):
#         if data_state['status_list'][i] == 1:
#             list_id_users.append(int(data_state['users_and_obs'][i]['chat_id']))
#
#     # Добавляем id админа
#     list_id_users.append(callback.message.chat.id)
#
#     await OrganizationExtend.update_by_id(
#         organization_id=data_state['id_organization'],
#         observers_id_list=list_id_users
#     )
#
#     await callback.message.edit_text(
#         text=text_end_change_observers_organization,
#         parse_mode="html"
#     )
