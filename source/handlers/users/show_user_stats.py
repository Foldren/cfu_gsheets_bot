from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsUserFilter
from components.keyboards_components.generators import get_inline_keyb_markup
from components.texts.users.show_user_stats import text_success_show_stats, text_no_shares_show_stats
from microservices.sql_models_extends.user import UserExtend

rt = Router()


# Хэндлер на команду /start
@rt.message(F.text == "Отчеты", IsUserFilter(), F.chat.type == "private")
async def show_user_stats(message: Message, state: FSMContext):
    await state.clear()

    stats_names = await UserExtend.get_user_periods_stats_list(message.from_user.id)

    if stats_names is None:
        await message.answer(text_no_shares_show_stats, parse_mode='html')
    else:
        admin_id = await UserExtend.get_user_admin_id(message.from_user.id)
        urls_stats = await UserExtend.get_admin_stats_urls(admin_id)

        keyboard = await get_inline_keyb_markup(
            list_names=stats_names,
            list_data=stats_names,
            callback_str="empty",
            number_cols=3,
            urls_list=urls_stats
        )

        await message.answer(text_success_show_stats, reply_markup=keyboard, parse_mode='html')


