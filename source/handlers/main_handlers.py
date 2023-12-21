from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.handlers import ErrorHandler
from aiogram.types import CallbackQuery

rt = Router()

rt.message.filter(F.chat.type == "private")
rt.callback_query.filter(F.message.chat.type == "private")


@rt.callback_query(F.data == 'disabled_inline_btn')
async def end_load_empty_button(callback: CallbackQuery):
    await callback.answer()
    return


# @rt.errors()
# async def errors_handler(exception: ErrorHandler):
#     print(exception.data)
