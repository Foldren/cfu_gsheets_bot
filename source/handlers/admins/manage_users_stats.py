from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.texts.admins.manage_user_stats import text_start_manage_stats, text_choose_observers_stats, \
    text_end_change_observers_p_stats
from components.filters import IsAdminFilter, IsAdminModeFilter
from components.keyboards_components.strings.inline import keyb_str_change_observers_ps
from components.tools import get_callb_content, generate_observers_list
from components.keyboards_components.generators import get_inline_keyb_markup
from config import STATS_UPRAVLYAIKA
from microservices.sql_models_extends.period_stat import PeriodStatExtend
from microservices.sql_models_extends.user import UserExtend
from states.admin.steps_manage_users_stats import StepsManageUsersStats

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter() and IsAdminModeFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter() and IsAdminModeFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Отчеты")
async def start_manage_users_stats(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StepsManageUsersStats.choose_stats_period)

    keyboard_stats = await get_inline_keyb_markup(
        list_names=STATS_UPRAVLYAIKA,
        list_data=STATS_UPRAVLYAIKA,
        callback_str="choose_stats_period",
        number_cols=3
    )

    await message.answer(text=text_start_manage_stats, reply_markup=keyboard_stats, parse_mode="html")


@rt.callback_query(StepsManageUsersStats.choose_stats_period, F.data.startswith("choose_stats_period"))
async def change_wallets_list(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsManageUsersStats.change_stats_observers)
    choose_period_stat_name = await get_callb_content(callback.data)
    admin_id = await UserExtend.get_user_admin_id(callback.from_user.id)
    users_and_obs = await PeriodStatExtend.get_period_stat_users_with_flag_observer(choose_period_stat_name, admin_id)
    status_list = await generate_observers_list(users_and_obs)
    list_index_users = []
    list_buttons_name = []

    # Генерируем список порядкового номера пользователей в клавиатуре
    for i in range(0, len(users_and_obs)):
        list_index_users.append(i)

    # Генерируем список наименований кнопок с пользователями
    for e in users_and_obs:
        status_emoji = "☑️" if e["observer"] else ""
        list_buttons_name.append(f'{status_emoji} {e["fullname"].split(" ")[1]} - {e["profession"]}')

    keyboard_users = await get_inline_keyb_markup(
        list_names=list_buttons_name,
        list_data=list_index_users,
        callback_str="change_observers_period_stat",
        number_cols=2,
        add_keyb_to_start=keyb_str_change_observers_ps
    )

    # Сохраняем название выбранного пункта и лист статусов пользователей (выбран или нет)
    await state.update_data({
        'period_stat_name': choose_period_stat_name,
        'list_index_users': list_index_users,
        'status_list': status_list,
        'users_and_obs': users_and_obs,
    })

    await callback.message.edit_text(
        text=text_choose_observers_stats,
        reply_markup=keyboard_users,
        parse_mode="html"
    )


@rt.callback_query(StepsManageUsersStats.change_stats_observers, F.data.startswith("change_observers_period_stat"))
async def change_observers_menu_item(callback: CallbackQuery, state: FSMContext):
    data_state = await state.get_data()
    number_choose_user = int(await get_callb_content(callback.data))
    data_state['status_list'][number_choose_user] = 1 if data_state['status_list'][number_choose_user] == 0 else 0
    list_names = []

    await state.update_data({
        'status_list': data_state['status_list'],
    })

    for i in range(0, len(data_state['users_and_obs'])):
        status_emoji = '' if data_state['status_list'][i] == 0 else '☑️'
        list_names.append(
            f'{status_emoji} {data_state["users_and_obs"][i]["fullname"].split(" ")[1]} - {data_state["users_and_obs"][i]["profession"]}')

    keyboard_users = await get_inline_keyb_markup(
        list_names=list_names,
        list_data=data_state['list_index_users'],
        callback_str="change_observers_menu_item",
        number_cols=2,
        add_keyb_to_start=keyb_str_change_observers_ps
    )

    await callback.message.edit_text(
        text=text_choose_observers_stats,
        reply_markup=keyboard_users,
        parse_mode="html"
    )


@rt.callback_query(StepsManageUsersStats.change_stats_observers, F.data == "save_change_observers_ps")
async def end_change_observers_menu_item(callback: CallbackQuery, state: FSMContext):
    data_state = await state.get_data()
    await state.clear()

    list_id_users = []

    # Генерируем список выбранных пользователей
    for i in range(0, len(data_state['users_and_obs'])):
        if data_state['status_list'][i] == 1:
            list_id_users.append(int(data_state['users_and_obs'][i]['chat_id']))

    # Добавляем id админа
    list_id_users.append(callback.message.chat.id)

    await PeriodStatExtend.update_observers_by_name(
        ps_name=data_state['period_stat_name'],
        observers_id_list=list_id_users
    )

    await callback.message.edit_text(
        text=text_end_change_observers_p_stats,
        parse_mode="html"
    )