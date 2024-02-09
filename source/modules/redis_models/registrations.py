from redis.asyncio import Redis


class RedisRegistration:
    redis_regs: Redis
    selected_bd: int
    __slots__ = ('redis_regs', 'selected_bd')

    def __init__(self, redis_regs: Redis):
        self.selected_bd = 1
        self.redis_regs = redis_regs

    async def check_registration_by_nickname(self, nickname: str):
        return await self.redis_regs.hgetall(nickname)

    async def set_new_registration(self, nickname: str, fullname: str,
                                   profession: str, id_admin: int, bet: int, increased_bet: int):
        await self.redis_regs.hset(nickname, mapping={
            "nickname": nickname,
            "fullname": fullname,
            "profession": profession,
            "id_admin": id_admin,
            "bet": bet,
            "increased_bet": increased_bet
        })

    async def get_registrations_params(self, nickname: str):
        return await self.redis_regs.hgetall(nickname)

    async def remove_registration(self, nickname_regs_user: str):
        await self.redis_regs.delete(nickname_regs_user)
