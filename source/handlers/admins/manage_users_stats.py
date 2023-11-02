from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.texts.admins.manage_user_stats import text_start_manage_stats, text_choose_observers_stats, \
    text_end_change_observers_p_stats
from components.filters import IsAdminFilter
from components.keyboards_components.inline_strings import keyb_str_change_observers_ps
from components.tools import get_callb_content, generate_observers_list, answer_or_edit_message, \
    get_users_keyb_names_with_checkbox, get_changed_reply_keyb_with_checkbox
from components.keyboards_components.generators import get_inline_keyb_markup
from config import STATS_UPRAVLYAIKA
from microservices.sql_models_extends.period_stat import PeriodStatExtend
from microservices.sql_models_extends.user import UserExtend
from states.admin.steps_manage_users_stats import StepsManageUsersStats

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsAdminFilter(), F.chat.type == "private")
rt.callback_query.filter(IsAdminFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Управление отчетами")
async def start_manage_users_stats(message: Message, state: FSMContext, answer_or_edit_msg: bool = True):
    await state.clear()
    await state.set_state(StepsManageUsersStats.choose_stats_period)

    keyboard_stats = await get_inline_keyb_markup(
        list_names=STATS_UPRAVLYAIKA,
        list_data=STATS_UPRAVLYAIKA,
        callback_str="choose_stats_period",
        number_cols=3
    )

    await answer_or_edit_message(
        message=message,
        text=text_start_manage_stats,
        keyboard_markup=keyboard_stats,
        flag_answer=answer_or_edit_msg
    )


@rt.callback_query(StepsManageUsersStats.choose_stats_period, F.data.startswith("choose_stats_period"))
async def change_stats_list(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsManageUsersStats.change_stats_observers)
    choose_period_stat_name = await get_callb_content(callback.data)
    await state.set_data({'stat_name': choose_period_stat_name})
    admin_id = await UserExtend.get_user_admin_id(callback.from_user.id)
    users_and_obs = await PeriodStatExtend.get_period_stat_users_with_flag_observer(choose_period_stat_name, admin_id)
    btns_ns_and_cbs = await get_users_keyb_names_with_checkbox(
        users=users_and_obs,
        flag_name="observer",
        flag_value=True,
    )

    keyboard_users = await get_inline_keyb_markup(
        list_names=btns_ns_and_cbs['names'],
        list_data=btns_ns_and_cbs['callbacks'],
        callback_str="change_observers_period_stat",
        number_cols=2,
        add_keyb_to_start=keyb_str_change_observers_ps
    )

    await callback.message.edit_text(
        text=text_choose_observers_stats,
        reply_markup=keyboard_users,
        parse_mode="html"
    )


@rt.callback_query(StepsManageUsersStats.change_stats_observers, F.data.startswith("change_observers_period_stat"))
async def change_observers_stat(callback: CallbackQuery):
    reply_keyboard = await get_changed_reply_keyb_with_checkbox(callback=callback)

    await callback.message.edit_text(
        text=text_choose_observers_stats,
        reply_markup=reply_keyboard,
        parse_mode="html"
    )


@rt.callback_query(StepsManageUsersStats.change_stats_observers, F.data == "save_change_observers_ps")
async def end_change_observers_stat(callback: CallbackQuery, state: FSMContext):
    st_data = await state.get_data()
    await state.clear()

    new_stat_observers_ids = []
    for i, row in enumerate(callback.message.reply_markup.inline_keyboard):
        for k, button in enumerate(row):
            if '☑️' in button.text:
                new_stat_observers_ids.append(int(button.callback_data.split(":")[1]))

    await PeriodStatExtend.update_observers_by_name(
        admin_id=callback.message.chat.id,
        ps_name=st_data['stat_name'],
        observers_id_list=new_stat_observers_ids
    )

    await callback.answer(text=text_end_change_observers_p_stats)
    await start_manage_users_stats(message=callback.message, state=state, answer_or_edit_msg=False)
