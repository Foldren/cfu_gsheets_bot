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

    async def get_users_statuses(self, users_id_list: list[str]):
        users_statuses = []
        for u_id in users_id_list:
            status = await self.redis_users.hget(u_id, 'status')
            users_statuses.append(int(status))
        return users_statuses

    async def reset_users_statuses(self, users_id_list: list[str]):
        for u_id in users_id_list:
            await self.redis_users.hset(u_id, 'status', '0')

    async def get_admin_mode(self, user_id: int):
        return await self.redis_users.hget(str(user_id), 'admin_mode')

    async def get_admin_time_status_refresh(self, admin_id: int):
        return await self.redis_users.hget(str(admin_id), 'date_status_refresh')

    async def set_admin_time_status_refresh(self, admin_id: int, date_refresh: str):
        return await self.redis_users.hset(str(admin_id), 'date_status_refresh', date_refresh)

    async def get_user_category(self, user_id: int):
        category = await self.redis_users.hget(str(user_id), 'category')
        return category

    async def get_user_admin_id(self, user_id: int):
        user = await self.redis_users.hgetall(str(user_id))
        return user_id if user['category'] == "admin" else user['admin_id']

    async def set_admin_mode(self, admin_id: int, mode: int):
        return await self.redis_users.hset(str(admin_id), 'admin_mode', str(mode))

    async def set_user_status(self, chat_id, status):
        return await self.redis_users.hset(str(chat_id), 'status', str(status))

    async def get_last_time_come_to_work(self, chat_id):
        return await self.redis_users.hget(str(chat_id), 'last_time_coming_to_work')

    async def set_last_time_come_to_work(self, chat_id, last_time):
        return await self.redis_users.hset(str(chat_id), 'last_time_coming_to_work', str(last_time))

    async def add_new_user(self, user_id: int, category: str, admin_id: int = None):
        map_ur = {
            "category": category,  # admin or user
            "status": '0',
            "last_time_coming_to_work": '',
        }

        if category == 'user':
            map_ur['admin_id'] = admin_id
        elif category == 'admin':
            map_ur['admin_mode'] = '1'
            map_ur["date_status_refresh"] = ''

        await self.redis_users.hset(str(user_id), mapping=map_ur)

    async def delete_users(self, list_id_users: list):
        await self.redis_users.delete(*list_id_users)
