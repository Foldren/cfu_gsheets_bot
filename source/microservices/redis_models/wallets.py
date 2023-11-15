from redis.asyncio import Redis


class RedisUserWallets:
    redis_wallets: Redis
    selected_bd: int
    __slots__ = ('redis_wallets', 'selected_bd')

    def __init__(self, redis_wallets: Redis):
        self.selected_bd = 2
        self.redis_wallets = redis_wallets

    async def get_wallets_list(self, user_id: int):
        wallets_hash = await self.redis_wallets.hgetall(str(user_id))
        wallets = list(wallets_hash.keys())
        return wallets if wallets else None

    async def set_new_wallets_list(self, user_id: int, wallets_list: list):
        wallets_dict = {}

        for e in wallets_list:
            wallets_dict[e] = ""

        try:
            await self.redis_wallets.delete(str(user_id))
        except Exception:
            pass
        await self.redis_wallets.hset(str(user_id), mapping=wallets_dict)

    async def delete(self, user_ids: list):
        await self.redis_wallets.delete(*user_ids)
