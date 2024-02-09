from models import ConfirmNotification


class ConfirmNotificationExtend:
    __slots__ = {}

    @staticmethod
    async def get(id_n) -> ConfirmNotification:
        return await ConfirmNotification.get(id=id_n)

    @staticmethod
    async def get_user_notifies_number(user_id):
        return await ConfirmNotification.filter(user__chat_id=user_id).count()

    @staticmethod
    async def delete_by_id(id_n):
        await ConfirmNotification.filter(id=id_n).delete()

