from redis.asyncio import Redis


class RedisUserReportCards:
    redis_wallets: Redis
    selected_bd: int
    __slots__ = ('redis_report_cards_users', 'selected_bd')

    def __init__(self, redis_report_cards_users: Redis):
        self.selected_bd = 3
        self.redis_report_cards_users = redis_report_cards_users

    async def get_wallets_list(self, user_id: int):
        wallets_hash = await self.redis_report_cards_users.hgetall(str(user_id))
        wallets = list(wallets_hash.keys())
        return wallets if wallets else None

    async def set_new_wallets_list(self, user_id: int, wallets_list: list):
        wallets_dict = {}

        for e in wallets_list:
            wallets_dict[e] = ""

        await self.redis_report_cards_users.delete(str(user_id))
        await self.redis_report_cards_users.hset(str(user_id), mapping=wallets_dict)

    async def delete(self, user_ids: list):
        await self.redis_report_cards_users.delete(*user_ids)
