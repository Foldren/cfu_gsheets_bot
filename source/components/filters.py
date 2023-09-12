from aiogram.filters import BaseFilter
from aiogram.types import Message, ChatMemberUpdated, CallbackQuery
from aioredis import Redis

from components.tools import get_callb_content
from services.models_extends.issuance_report import IssuanceReportApi
from services.models_extends.notify_group import NotifyGroupApi
from services.redis_extends.registrations import RedisRegistration
from services.redis_extends.user import RedisUser


class IsAdminFilter(BaseFilter):
    async def __call__(self, message: Message, redis_users: RedisUser) -> bool:
        status = await redis_users.get_user_status(message.from_user.id)
        return (status == 1) or (status == 0)


class IsUserFilter(BaseFilter):
    async def __call__(self, message: Message, redis_users: RedisUser) -> bool:
        status = await redis_users.get_user_status(message.from_user.id)
        return (status != 1) and (status is not None)


class IsRegistration(BaseFilter):
    async def __call__(self, message: Message, redis_regs: RedisRegistration) -> bool:
        registration = await redis_regs.check_registration_by_nickname(message.from_user.username)
        return registration is not None


class IsSenderMemberFilter(BaseFilter):
    async def __call__(self, event: ChatMemberUpdated, redis_users: RedisUser) -> bool:
        status = await redis_users.get_user_status(event.from_user.id)
        return status is not None


class IsSenderGroupExistFilter(BaseFilter):
    async def __call__(self, event: ChatMemberUpdated) -> bool:
        return await NotifyGroupApi.check_exists_by_chat_id_group(chat_id_group=event.chat.id)


# Фильтр на проверку кто подтверждает выдачу под отчет
class IsConfirmFromNecUser(BaseFilter):
    async def __call__(self, callback: CallbackQuery) -> bool:
        username = "@" + callback.message.from_user.username
        id_report = await get_callb_content(callback.data)
        return await IssuanceReportApi.check_issuance_report_by_nickname_and_id(
            recipient_nickname=username,
            id_issuance_report=id_report
        )

