from models import User, AdminInfo


class UserApi:
    @staticmethod
    async def get_admin_info(admin_id):
        return await AdminInfo.get(admin_id=admin_id)

    @staticmethod
    async def get_admins_id_list():
        return await User.filter(admin_id=None).all().values_list("chat_id", flat=True)

    @staticmethod
    async def get_users_id_list():
        return await User.exclude(admin_id=None).all().values_list("chat_id", flat=True)

    @staticmethod
    async def get_members_id_list():
        return await User.all().values_list("chat_id", flat=True)

    @staticmethod
    async def get_by_id(id_user: int) -> User:
        return await User.filter(chat_id=id_user).first()

    @staticmethod
    async def get_user_admin_id(id_user: int) -> int:
        values_user = await User.get(chat_id=id_user).values("admin_id")
        return values_user['admin_id']

    @staticmethod
    async def get_admin_users(id_admin: int):
        return await User.filter(admin_id=id_admin).all().values("nickname", "fullname", "profession", "chat_id")

    @staticmethod
    async def add(chat_id: int, nickname: str, fullname: str, profession: str, id_admin: int):
        await User.create(chat_id=chat_id, nickname=nickname, fullname=fullname, profession=profession,
                          admin_id=id_admin)

    @staticmethod
    async def update_by_id(chat_id: int, nickname: str = None, fullname: str = None, profession: str = None,
                           id_admin: int = None, new_chat_id: int = None):
        user = await User.get(chat_id=chat_id)

        user.chat_id = chat_id if new_chat_id is None else new_chat_id

        if nickname is not None:
            user.nickname = nickname
        if fullname is not None:
            user.fullname = fullname
        if profession is not None:
            user.profession = profession
        if id_admin is not None:
            user.id_admin = id_admin

        await user.save()

    @staticmethod
    async def delete_users_by_chat_ids(chat_ids_users_list: list):
        await User.filter(chat_id__in=chat_ids_users_list).delete()