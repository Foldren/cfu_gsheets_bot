from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter, IsNotMainMenuMessage
from components.keyboards_components.generators import get_inline_keyb_markup
from components.text_generators.users import get_msg_notify_new_transfer
from components.texts.users.write_category_to_bd import text_invalid_volume_operation, text_no_menu_items_orgs
from components.texts.users.write_transfer_to_wallet_to_bd import text_set_volume_transfer, text_select_wallet_sender, \
    text_select_wallet_recipient, text_end_transfer, text_start_transfer
from components.tools import get_callb_content, send_multiply_messages
from microservices.google_api.google_table import GoogleTable
from microservices.redis_models.user import RedisUser
from microservices.redis_models.wallets import RedisUserWallets
from microservices.sql_models_extends.notify_group import NotifyGroupExtend
from microservices.sql_models_extends.organization import OrganizationExtend
from microservices.sql_models_extends.user import UserExtend
from states.user.steps_create_notes_to_bd import StepsWriteTransfer

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Перевод на кошелек")
async def start_write_new_report_type_user(message: Message, state: FSMContext, redis_users: RedisUser):
