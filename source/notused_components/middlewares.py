from typing import Callable, Dict, Any, Awaitable
from aiogram import BaseMiddleware
from aiogram.types import Message


# class ChangeNumberNotifiesMiddleware(BaseMiddleware):
#     async def __call__(
#             self,
#             handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
#             event: Message,
#             data: Dict[str, Any]
#     ) -> Any:
#         print(event.reply_markup)
#         # Для выполнения хендлера возвращаем
#         return await handler(event, data)
