from aiogram.filters import ChatMemberUpdatedFilter, MEMBER, LEFT
from aiogram.types import ChatMemberUpdated
from aiogram import Router, F
from components.filters import IsSenderMemberFilter, IsSenderGroupExistFilter
from components.texts import text_success_join_bot_to_group
from services.database_extends.notify_group import NotifyGroupApi
from services.database_extends.user import UserApi

rt = Router()


@rt.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=MEMBER), IsSenderMemberFilter(), F.chat.type == "group")
async def join_to_notification_group(event: ChatMemberUpdated):
    current_user = await UserApi.get_by_id(event.from_user.id)
    admin = await current_user.admin
    admin_id = event.from_user.id if admin is None else admin.chat_id

    # Прикрепляем группу к админу
    await NotifyGroupApi.attach_group_to_admin(admin_id=admin_id, chat_id_group=event.chat.id)

    await event.answer(text_success_join_bot_to_group, parse_mode='html')


# Удаляем связь админа с группой в случае если бота кикнут
@rt.my_chat_member(ChatMemberUpdatedFilter(member_status_changed=LEFT), IsSenderGroupExistFilter(), F.chat.type == "group")
async def kicked_from_notification_group(event: ChatMemberUpdated):
    await NotifyGroupApi.detach_group_from_admin(event.chat.id)
