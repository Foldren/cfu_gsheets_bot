from redis.asyncio import Redis


class RedisUserRepsReqs:
    redis_users: Redis
    selected_bd: int
    __slots__ = ('redis_users', 'selected_bd')

    def __init__(self, redis_users: Redis):
        self.selected_bd = 0
        self.redis_users = redis_users

    async def get_user_status(self, user_id: int, invert: bool = False):
        status = await self.redis_users.get(str(user_id))
        if status is not None:
            status = int(not int(status)) if invert else int(status)
            return int(status)
        else:
            return None

    async def get_user_admin_id(self, user_id: int):
        admin_id = await self.redis_users.get(str(user_id))
        return user_id if admin_id == "0" else admin_id

    async def set_admin_status(self, admin_id: int, admin_status: int):
        return await self.redis_users.set(str(admin_id), str(admin_status))

    async def add_new_user(self, user_id: int, admin_id: int = None):
        status_user = 1 if admin_id is None else admin_id
        await self.redis_users.set(str(user_id), str(status_user))

    async def delete_users(self, list_id_users: list):
        await self.redis_users.delete(*list_id_users)
