from aiogram.types import CallbackQuery
from aiogram import Router, F, Bot
from aiogram.types import CallbackQuery
from components.filters import IsConfirmFromNecUser
from components.tools import get_callb_content
from components.users.texts import text_confirm_issuance_report
from services.google_api.google_table import GoogleTable
from services.models_extends.issuance_report import IssuanceReportApi
from services.models_extends.user import UserApi

rt = Router()


@rt.callback_query(IsConfirmFromNecUser(), F.message.chat.type == "group", F.data.startswith("confirm_issuance"))
async def confirm_issuance_report(callback: CallbackQuery, gt_object: GoogleTable, bot_object: Bot):
    print()
    # issuance_report_id = await get_callb_content(callback.data)
    # issuance_report = await IssuanceReportApi.get_issuance_report_by_id(issuance_report_id)
    # admin_id = await UserApi.get_user_admin_id(issuance_report.user_id)
    # table_url = await UserApi.get_table_url(admin_id)
    # recipient = await UserApi.get_by_nickname(issuance_report.selected_user_nickname)
    #
    # # Вносим в google таблицу запись
    # await gt_object.add_issuance_report_to_bd(
    #     table_url=table_url,
    #     chat_id_worker=issuance_report.user_id,
    #     fullname_recipient=recipient.fullname,
    #     volume_op=issuance_report.volume,
    #     payment_method=issuance_report.payment_method
    # )
    #
    # # Удаляем сообщение
    # await bot_object.delete_message(issuance_report.notify_group_id, issuance_report.message_id)
    #
    # # Сообщаем об успешной записи в бд
    # await bot_object.send_message(chat_id=issuance_report.notify_group_id, text=text_confirm_issuance_report)
    #
    # # Удаляем запись из бд о выдаче под отчет
    # await IssuanceReportApi.remove_issuance_report_by_id(issuance_report_id)




