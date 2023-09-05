import asyncio
import logging
from aiogram import Bot, Dispatcher
from tortoise import run_async
from handlers.admins import start_admin
from handlers.admins.manage_menu_items import get_list_menu_items, add_menu_item, change_menu_item, delete_menu_item
from config import TOKEN
from handlers.admins.manage_users import get_list_users, add_user, change_user, delete_user
from handlers.users import browse_menu_items, start_user, write_menu_item_to_bd, join_to_notification_group
from init_db import init_db
from services.google_api.google_table import GoogleTable

admin_routers = [
    start_admin.rt, get_list_menu_items.rt, add_menu_item.rt, get_list_users.rt, add_user.rt,
    change_user.rt, change_menu_item.rt, delete_menu_item.rt, delete_user.rt
]

user_routers = [
    start_user.rt, browse_menu_items.rt, write_menu_item_to_bd.rt, join_to_notification_group.rt
]


# Запуск процесса поллинга новых апдейтов
async def main():
    # Объект бота
    bot = Bot(token=TOKEN)
    # Диспетчер
    dp = Dispatcher()
    # Включаем логирование, чтобы не пропустить важные сообщения

    logging.basicConfig(level=logging.INFO)
    dp.include_routers(*admin_routers, *user_routers)

    google_table = GoogleTable()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, bot_object=bot, gt_object=google_table)


if __name__ == "__main__":
    run_async(init_db())
    asyncio.run(main())


