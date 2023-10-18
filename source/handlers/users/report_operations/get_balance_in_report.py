from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsUserFilter
from components.texts.users.get_balance_in_report import text_user_balances, text_no_reports, text_load_balances
from microservices.google_api.google_table import GoogleTable
from microservices.redis_models.user import RedisUser
from microservices.sql_models_extends.user import UserExtend

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Остаток в подотчете")
async def get_balance_in_report(message: Message, state: FSMContext, gt_object: GoogleTable, redis_users: RedisUser):
    await state.clear()
    new_message = await message.answer(text=text_load_balances, parse_mode="html")
    admin_id = await redis_users.get_user_admin_id(message.from_user.id)
    admin_info = await UserExtend.get_admin_info(admin_id)
    text_balances = text_user_balances + "\n"

    balances = await gt_object.get_balance_in_report_by_fullname(
        table_encr_url=admin_info.google_table_url,
        chat_id_user=message.from_user.id
    )

    if balances:
        balances.sort(key=lambda e: e[0])

        last_org = ""
        for b in balances:
            if b[0] != last_org:
                text_balances += f"\n<b>⤵️ {b[0]}</b>\n<u>{b[1]}:</u>  <code>{b[2]}</code> руб.\n"
                last_org = b[0]
            else:
                text_balances += f"<u>{b[1]}:</u>  <code>{b[2]}</code> руб.\n"

        await new_message.edit_text(text=text_balances, parse_mode="html")

    else:
        await new_message.edit_text(text=text_no_reports, parse_mode="html")
