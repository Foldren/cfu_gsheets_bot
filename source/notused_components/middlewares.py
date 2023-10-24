from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


# class IsMemberMiddleWare(BaseMiddleware):
#     async def __call__(
#             self,
#             handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
#             event: Message,
#             data: Dict[str, Any]
#     ) -> Any:
#         status = await data['redis_users'].get_user_category(event.from_user.id)
#         print(status)
#         if status is not None:
#             # Для выполнения хендлера возвращаем
#             return await handler(event, data)
