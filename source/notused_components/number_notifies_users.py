# from redis.asyncio import Redis
#
#
# class RedisNotifies:
#     redis_notfs: Redis
#     selected_bd: int
#     __slots__ = ('redis_notfs', 'selected_bd')
#
#     def __init__(self, redis_regs: Redis):
#         self.selected_bd = 3
#         self.redis_notfs = redis_regs
#
#     async def get_user_number_notifies(self, chat_id: str):
#         return await self.redis_notfs.get(chat_id)
