from aiogram.filters import ChatMemberUpdatedFilter, MEMBER, LEFT
from aiogram.types import ChatMemberUpdated
from aiogram import Router, F
from components.filters import IsSenderMemberFilter, IsSenderGroupExistFilter
from components.texts.users.check_events_notifications_group import text_success_join_bot_to_group
from config import TECHNICAL_SUPPORT_GROUP_CHAT_ID
from microservices.sql_models_extends.notify_group import NotifyGroupExtend
from microservices.sql_models_extends.user import UserExtend

rt = Router()


@rt.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER), IsSenderMemberFilter(),
                   F.chat.type == "group", F.chat.id != TECHNICAL_SUPPORT_GROUP_CHAT_ID)
async def join_to_notification_group(event: ChatMemberUpdated):
    current_user = await UserExtend.get_by_id(event.from_user.id)
    admin = await current_user.admin
    admin_id = event.from_user.id if admin is None else admin.chat_id

    # Прикрепляем группу к админу
    await NotifyGroupExtend.attach_group_to_admin(admin_id=admin_id, chat_id_group=event.chat.id, name_group=event.chat.full_name)

    await event.answer(text_success_join_bot_to_group, parse_mode='html')


# Удаляем связь админа с группой в случае если бота кикнут
@rt.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEFT), IsSenderGroupExistFilter(),
                   F.chat.type == "group", F.chat.id != TECHNICAL_SUPPORT_GROUP_CHAT_ID)
async def kicked_from_notification_group(event: ChatMemberUpdated):
    await NotifyGroupExtend.detach_group_from_admin(event.chat.id)
