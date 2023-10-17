from models import ConfirmNotification


class ConfirmNotificationExtend:
    __slots__ = {}

    @staticmethod
    async def get(id_n) -> ConfirmNotification:
        return await ConfirmNotification.get(id=id_n)

    @staticmethod
    async def delete_by_id(id_n):
        await ConfirmNotification.filter(id=id_n).delete()

