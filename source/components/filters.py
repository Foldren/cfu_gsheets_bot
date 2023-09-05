from aiogram.filters import BaseFilter
from aiogram.types import Message, ChatMemberUpdated
from services.database_extends.notify_group import NotifyGroupApi
from services.database_extends.user import UserApi


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in await UserApi.get_admins_id_list()


class IsUserFilter(BaseFilter):
    async def __call__(self, message: Message) -> bool:
        return message.from_user.id in await UserApi.get_users_id_list()


class IsSenderMemberFilter(BaseFilter):
    async def __call__(self, event: ChatMemberUpdated) -> bool:
        return event.from_user.id in await UserApi.get_members_id_list()


class IsSenderGroupExistFilter(BaseFilter):
    async def __call__(self, event: ChatMemberUpdated) -> bool:
        return await NotifyGroupApi.check_exists_by_chat_id_group(chat_id_group=event.chat.id)


