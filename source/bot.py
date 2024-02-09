import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from redis.asyncio import from_url
from tortoise import run_async
from config import TOKEN, REDIS_URL
from handlers import main_handlers
from handlers.admins import start_admin, change_mode, manage_users_stats, open_admin_nested_menu, \
    manage_users_roles
from handlers.admins.manage_banks import get_list_banks, add_bank, delete_banks
from handlers.admins.manage_categories import get_list_categories, add_category, change_category, delete_category
from handlers.admins.manage_organizations import get_list_organizations, add_organization, \
    delete_organizations
from handlers.admins.manage_partners import get_list_partners, add_partner, delete_partners
from handlers.admins.manage_payment_accounts import get_list_payment_accounts, add_payment_account, \
    delete_payment_accounts
from handlers.admins.manage_users import get_list_users, add_user, change_user, delete_user
from handlers.members import check_events_notification_groups, confirm_issuance_report, technical_support, \
    manage_confirm_notifications
from handlers.members.timekeepers import write_new_report_card_user
from handlers.super_admin import add_new_client
from handlers.users import start_user, open_nested_menu, show_user_stats, request_money_report
from handlers.users.categories_operations import browse_categories, write_chosen_category_to_bd, \
    choose_write_category_sender
from handlers.users.report_operations import write_issuance_of_report_to_bd, write_return_of_report_to_bd, \
    get_balance_in_report
from handlers.users.wallets_operations import change_wallets_list, write_transfer_to_wallet_to_bd
from init_db import init_db
from modules.google_api.google_drive import GoogleDrive
from modules.google_api.google_table import GoogleTable
from modules.redis_models.registrations import RedisRegistration
from modules.redis_models.user import RedisUser
from modules.redis_models.wallets import RedisUserWallets

admin_routers = [
    start_admin.rt, get_list_categories.rt, add_category.rt, get_list_users.rt, add_user.rt,
    change_user.rt, change_category.rt, delete_category.rt, delete_user.rt, change_mode.rt,
    manage_users_stats.rt, get_list_organizations.rt, add_organization.rt, delete_organizations.rt,
    get_list_partners.rt, add_partner.rt, delete_partners.rt, get_list_banks.rt, add_bank.rt, delete_banks.rt,
    get_list_payment_accounts.rt, add_payment_account.rt, delete_payment_accounts.rt, manage_users_roles.rt
]

user_routers = [
    start_user.rt, browse_categories.rt, write_chosen_category_to_bd.rt, write_issuance_of_report_to_bd.rt,
    write_return_of_report_to_bd.rt, choose_write_category_sender.rt, write_transfer_to_wallet_to_bd.rt,
    open_nested_menu.rt, change_wallets_list.rt, show_user_stats.rt, get_balance_in_report.rt,
    open_admin_nested_menu.rt, request_money_report.rt
]

member_routers = [
    check_events_notification_groups.rt, confirm_issuance_report.rt, technical_support.rt,
    manage_confirm_notifications.rt, write_new_report_card_user.rt
]

super_admin_routers = [
    add_new_client.rt
]


# Запуск процесса поллинга новых апдейтов
async def main():
    # Объект бота
    bot = Bot(token=TOKEN, parse_mode='html')
    # Диспетчер

    # В 15 db будут стейты
    storage = RedisStorage(await from_url(REDIS_URL, db=15, decode_responses=True))
    dp = Dispatcher(storage=storage)

    # Включаем логирование, чтобы не пропустить важные сообщения
    logging.basicConfig(level=logging.INFO)
    dp.include_routers(*admin_routers, *user_routers, *member_routers, main_handlers.rt, *super_admin_routers)

    google_table = GoogleTable()

    google_drive = GoogleDrive()

    redis_status_users = RedisUser(await from_url(REDIS_URL, db=0, decode_responses=True))
    # chat-id -> 0 / 1 / chat_id_admin

    redis_registrations_users = RedisRegistration(await from_url(REDIS_URL, db=1, decode_responses=True))
    # chat_id -> hash {chat_id, name, profession, admin_id}

    redis_wallets_users = RedisUserWallets(await from_url(REDIS_URL, db=2, decode_responses=True))
    # chat_id -> hash {bank1, bank2,..}

    # ЮЗЕР: При добавлении нового юзера нужно добавить ему хотя бы один кошелек
    # в redis_wallets_users и запись со статусом в redis_status_users, а также две роли
    # типов 'report_request' и 'normal'
    #
    # АДМИН: При добавлении админа нужно добавить его в redis_status_users category='admin', status='0',
    # admin_mode = '1', date_status_refresh='', определить для него ссылки на гугл таблицу и гугл драйв, добавить ему
    # один кошелек в redis_wallets_users и добавить ему все 3 периода по отчетам и dashboard в sql
    # period_stats_observers, также создать папку для чеков в misc, а также создать две роли типов
    # 'report_request' и 'normal' (в папку поместить файл)

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot,
                           bot_object=bot,
                           gt_object=google_table,
                           gd_object=google_drive,
                           redis_users=redis_status_users,
                           redis_regs=redis_registrations_users,
                           redis_wallets=redis_wallets_users,
                           allowed_updates=["message", "callback_query", "my_chat_member"]
                           )


if __name__ == "__main__":
    run_async(init_db())
    asyncio.run(main())


