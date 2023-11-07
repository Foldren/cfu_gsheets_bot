from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from cryptography.fernet import Fernet

from components.filters import IsUserFilter
from components.keyboards_components.generators import get_inline_keyb_markup, get_dashb_checks_row, \
    get_dashboard_url_keyb_markup
from components.text_generators.users import get_text_dashboard_message
from components.texts.users.show_user_stats import text_success_show_stats, text_no_shares_show_stats
from config import SECRET_KEY
from microservices.google_api.google_table import GoogleTable
from microservices.redis_models.user import RedisUser
from microservices.sql_models_extends.user import UserExtend
from states.user.steps_show_user_stats import StepsShowUserStats

rt = Router()


# Хэндлер на команду /start
@rt.message(F.text == "Отчеты", IsUserFilter(), F.chat.type == "private")
async def show_user_stats(message: Message, state: FSMContext, gt_object: GoogleTable, redis_users: RedisUser):
    """
    Обработчик на получение списка отчетов (ежедневный, еженедельный..) расшареных юзеру
    """
    await state.clear()
    await state.set_state(StepsShowUserStats.show_main_stats)

    stats_names = await UserExtend.get_user_periods_stats_list(message.from_user.id)
    admin_id = await redis_users.get_user_admin_id(message.from_user.id)
    admin_info = await UserExtend.get_admin_info(admin_id)

    if stats_names:
        admin_id = await UserExtend.get_user_admin_id(message.from_user.id)
        urls_stats = await UserExtend.get_admin_stats_urls_by_names(admin_id, stats_names, gt_object, message)
        google_checks_url = Fernet(SECRET_KEY).decrypt(admin_info.google_drive_dir_url).decode("utf-8")

        upper_btns = []
        btns_names = []
        for s in stats_names:
            if s in ["Dashboard", "Чеки"]:
                upper_btns.append(s)
            else:
                btns_names.append(s)

        keyboard = await get_inline_keyb_markup(
            list_names=btns_names,
            callback_str="disabled_inline_btn",
            number_cols=3,
            urls_list=urls_stats,
            add_keyb_to_start=await get_dashb_checks_row(upper_btns, google_checks_url)
        )

        await message.answer(text_success_show_stats, reply_markup=keyboard, parse_mode='html')
    else:
        await message.answer(text_no_shares_show_stats, parse_mode='html')


@rt.callback_query(StepsShowUserStats.show_main_stats, F.data == "open_dashboard")
async def show_dashboard(callback: CallbackQuery, state: FSMContext, gt_object: GoogleTable, redis_users: RedisUser):
    await state.clear()
    await callback.message.edit_text(text="Подгружаю Dashboard ⏳")
    admin_id = await redis_users.get_user_admin_id(callback.message.chat.id)
    admin_info = await UserExtend.get_admin_info(admin_id)
    dashboard_stats = await gt_object.get_dashboard(admin_info.google_table_url)
    msg_text = await get_text_dashboard_message(dashboard_stats)
    decr_dashboard_url = Fernet(SECRET_KEY).decrypt(admin_info.gt_dashboard_url).decode("utf-8")
    keyb_markup = await get_dashboard_url_keyb_markup(decr_dashboard_url)
    await callback.message.edit_text(text=msg_text, reply_markup=keyb_markup)


