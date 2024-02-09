from models import NotifyGroup, User


class NotifyGroupExtend:
    __slots__ = {}

    @staticmethod
    async def attach_group_to_admin(admin_id: int, chat_id_group: int, name_group: str):
        await NotifyGroup.create(admin_id=admin_id, chat_id=chat_id_group, name=name_group)

    @staticmethod
    async def detach_group_from_admin(chat_id_group: int):
        await NotifyGroup.filter(chat_id=chat_id_group).delete()

    @staticmethod
    async def check_exists_by_chat_id_group(chat_id_group: int):
        return await NotifyGroup.exists(chat_id=chat_id_group)

    @staticmethod
    async def get_admin_notify_groups_chat_ids(admin_id: int):
        admin = await User.get(chat_id=admin_id)
        admin_groups_ids_list = await admin.notify_groups.all().values_list("chat_id", flat=True)
        return admin_groups_ids_list

    @staticmethod
    async def check_admin_groups_empty(admin_id):
        admin = await User.get(chat_id=admin_id)
        admin_ngroups = await admin.notify_groups
        return (admin_ngroups is None) or (admin_ngroups == [])

