from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsUserFilter
from components.texts.users.request_money_report import text_start_request_money_report, text_send_request_to_agreement
from components.tools import get_msg_list_data
from states.admin.steps_manage_reports_requests import StepsMakeRequestMoneyReport

rt = Router()

# Ставим на роутер фильтры (приватный чат + категория пользователя)
rt.message.filter(IsUserFilter(), F.chat.type == "private")
rt.callback_query.filter(IsUserFilter(), F.message.chat.type == "private")


@rt.message(F.text == "Запрос денег в подотчет")
async def start_request_money_report(message: Message, state: FSMContext) -> None:
    """
    Обработчик на начало операции запроса денег в подотчет (первый шаг - ввод суммы и комментария)

    :param message: сообщение из главного меню
    :param state: стейт главного меню
    """
    await state.clear()
    await state.set_state(StepsMakeRequestMoneyReport.start_agreement)
    await message.answer(text=text_start_request_money_report)


@rt.message(StepsMakeRequestMoneyReport.start_agreement)
async def send_request_to_agreement(message: Message, state: FSMContext) -> None:
    msg_data = await get_msg_list_data(message.text)
    await message.answer(text=text_send_request_to_agreement)




