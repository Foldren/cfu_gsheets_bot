from redis.asyncio import Redis


class RedisUser:
    redis_users: Redis
    selected_bd: int
    __slots__ = ('redis_users', 'selected_bd')

    def __init__(self, redis_users: Redis):
        self.selected_bd = 0
        self.redis_users = redis_users

    async def get_user(self, user_id: int):
        return await self.redis_users.hgetall(str(user_id))

    async def get_admin_status(self, user_id: int):
        return await self.redis_users.hget(str(user_id), 'status')

    async def get_user_category(self, user_id: int):
        category = await self.redis_users.hget(str(user_id), 'category')
        return category

    async def get_user_admin_id(self, user_id: int):
        user = await self.redis_users.hgetall(str(user_id))
        return user_id if user['category'] == "admin" else user['admin_id']

    async def set_admin_status(self, admin_id: int, admin_status: int):
        return await self.redis_users.hset(str(admin_id), 'status', str(admin_status))

    async def add_new_user(self, user_id: int, category: str, admin_id: int = None):
        await self.redis_users.hset(str(user_id), mapping={
            "category": category,  # admin or user
            "admin_id": '' if category != 'user' else admin_id,
            "status": '' if category != 'admin' else '1',
            "active_reply_markup": '',
        })

    async def delete_users(self, list_id_users: list):
        await self.redis_users.delete(*list_id_users)
