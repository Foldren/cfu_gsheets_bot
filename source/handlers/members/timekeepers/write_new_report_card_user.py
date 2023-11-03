from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsTimeKeeperFilter
from components.keyboards_components.generators import get_inline_keyb_markup
from components.texts.members.write_new_report_card_user import text_start_write_new_report_type_user
from components.tools import get_callb_content
from config import DEFINE_STATUSES
from microservices.google_api.google_table import GoogleTable
from microservices.redis_models.user import RedisUser
from microservices.sql_models_extends.user import UserExtend
from states.member.steps_write_report_card import StepsWriteReportCard
from datetime import datetime, timedelta

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsTimeKeeperFilter(), F.chat.type == "private")
rt.callback_query.filter(IsTimeKeeperFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Табель")
async def start_write_new_report_type_user(message: Message, state: FSMContext, redis_users: RedisUser):
    await state.clear()
    await state.set_state(StepsWriteReportCard.change_user_type_report_card)
    admin_id = await redis_users.get_user_admin_id(message.from_user.id)
    time_status_refresh = await redis_users.get_admin_time_status_refresh(admin_id)
    fst_load = False
    d_now = datetime.now()
    d_refresh = d_now + timedelta(days=1)
    dt_refresh = datetime(year=d_refresh.year, month=d_refresh.month, day=d_refresh.day, hour=0, minute=0)

    try:
        date_refresh = datetime.strptime(time_status_refresh, '%d:%m:%Y-%H:%M')
        if date_refresh < datetime.now():
            fst_load = True
            users_ids = await UserExtend.get_admin_users(admin_id, include_admin=True, only_ids=True)
            await redis_users.reset_users_statuses(users_ids)
            await redis_users.set_admin_time_status_refresh(admin_id, dt_refresh.strftime('%d:%m:%Y-%H:%M'))

    except ValueError:
        await redis_users.set_admin_time_status_refresh(admin_id, dt_refresh.strftime('%d:%m:%Y-%H:%M'))

    users = await UserExtend.get_admin_users(admin_id, include_admin=True)
    users_ids = [str(u['chat_id']) for u in users]
    users_statuses = await redis_users.get_users_statuses(users_ids)

    list_names = []
    for key, u in enumerate(users):
        status_u = DEFINE_STATUSES[0] if fst_load else DEFINE_STATUSES[users_statuses[key]]
        list_names.append(f"{status_u} {u['fullname'].split(' ')[1]} - {u['profession']}")

    keyboard_markup = await get_inline_keyb_markup(
        callback_str='report_card',
        number_cols=1,
        list_names=list_names,
        list_data=[u['chat_id'] for u in users]
    )
    await message.answer(text=text_start_write_new_report_type_user, reply_markup=keyboard_markup)


@rt.callback_query(StepsWriteReportCard.change_user_type_report_card, F.data.startswith('report_card'))
async def change_type_report_card_user(callback: CallbackQuery, gt_object: GoogleTable, redis_users: RedisUser):
    user_id = await get_callb_content(callback.data)
    user = await UserExtend.get_by_id(user_id)
    admin_id = await redis_users.get_user_admin_id(callback.message.chat.id)
    admin_info = await UserExtend.get_admin_info(admin_id)
    keyboard_markup = callback.message.reply_markup

    for i, row in enumerate(keyboard_markup.inline_keyboard):
        for k, button in enumerate(row):
            if button.callback_data == callback.data:
                current_status = button.text.split(":")[0] + ":"
                status_number = DEFINE_STATUSES.index(current_status)
                if status_number != 2:
                    keyboard_markup.inline_keyboard[i][k].text = DEFINE_STATUSES[status_number + 1] + \
                                                                 " " + button.text.split(":")[1][1:]
                    user_id = button.callback_data.split(":")[1]
                    if (status_number + 1) == 1:
                        await redis_users.set_last_time_come_to_work(user_id, datetime.now().strftime('%d.%m.%Y-%H:%M'))
                    last_time_come_to_work = await redis_users.get_last_time_come_to_work(user_id)
                    await redis_users.set_user_status(user_id, status_number + 1)
                    await gt_object.write_new_report_card_user(
                        table_encr_url=admin_info.google_table_url,
                        chat_id_user=int(user_id),
                        name_user=user.fullname,
                        status_i=status_number + 1,
                        bet=user.bet,
                        increased_bet=user.increased_bet,
                        last_time_come_to_work=last_time_come_to_work,
                    )
                else:
                    await callback.answer("⛔️ Последний статус. Обновление в 00:00")

    await callback.message.edit_text(text=text_start_write_new_report_type_user, reply_markup=keyboard_markup)


