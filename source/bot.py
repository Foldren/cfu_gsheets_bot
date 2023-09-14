import asyncio
import logging
from aiogram import Bot, Dispatcher
from aioredis import from_url
from tortoise import run_async
from handlers.admins import start_admin, change_mode
from handlers.admins.manage_menu_items import get_list_menu_items, add_menu_item, change_menu_item, delete_menu_item
from config import TOKEN, REDIS_URL
from handlers.admins.manage_users import get_list_users, add_user, change_user, delete_user
from handlers.users import start_user, issuance_of_report, \
    return_issuance_means, make_transfer, open_nested_menu, change_wallets_list
from handlers.users.write_menu_item_to_bd import browse_menu_items, write_menu_item_to_bd, \
    choose_write_menu_item_sender
from handlers.members import join_to_notification_group, confirm_issuance_report
from init_db import init_db
from services.google_api.google_drive import GoogleDrive
from services.google_api.google_table import GoogleTable
from services.redis_extends.registrations import RedisRegistration
from services.redis_extends.user import RedisUser
from services.redis_extends.wallets import RedisUserWallets

admin_routers = [
    start_admin.rt, get_list_menu_items.rt, add_menu_item.rt, get_list_users.rt, add_user.rt,
    change_user.rt, change_menu_item.rt, delete_menu_item.rt, delete_user.rt, change_mode.rt
]

user_routers = [
    start_user.rt, browse_menu_items.rt, write_menu_item_to_bd.rt, issuance_of_report.rt,
    return_issuance_means.rt, choose_write_menu_item_sender.rt, make_transfer.rt, open_nested_menu.rt,
    change_wallets_list.rt
]

member_routers = [
    join_to_notification_group.rt, confirm_issuance_report.rt
]


# Запуск процесса поллинга новых апдейтов
async def main():
    # Объект бота
    bot = Bot(token=TOKEN)
    # Диспетчер
    dp = Dispatcher()
    # Включаем логирование, чтобы не пропустить важные сообщения

    logging.basicConfig(level=logging.INFO)
    dp.include_routers(*admin_routers, *user_routers, *member_routers)

    google_table = GoogleTable()
    google_drive = GoogleDrive()

    redis_status_users = RedisUser(await from_url(REDIS_URL, db=0, decode_responses=True))
    # chat-id -> 0 / 1 / chat_id_admin

    redis_registrations_users = RedisRegistration(await from_url(REDIS_URL, db=1, decode_responses=True))
    # chat_id -> hash {chat_id, name, profession, admin_id}

    redis_wallets_users = RedisUserWallets(await from_url(REDIS_URL, db=2, decode_responses=True))
    # chat_id -> hash {bank1, bank2,..}

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


