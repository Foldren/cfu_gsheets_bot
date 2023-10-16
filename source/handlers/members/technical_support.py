from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from components.filters import IsSenderMemberFilter
from components.texts.members.technical_support import text_start_write_message_to_support, text_end_send_msg_to_support
from config import TECHNICAL_SUPPORT_GROUP_CHAT_ID
from states.member.steps_technical_support import StepsTechnicalSupport

rt = Router()

rt.message.filter(IsSenderMemberFilter(), F.chat.type == "private")
rt.callback_query.filter(IsSenderMemberFilter(), F.chat.type == "private")


@rt.message(F.text == "Поддержка")
async def send_message_to_technical_support(message: Message, state: FSMContext):
    await state.clear()
    await state.set_state(StepsTechnicalSupport.start_write_message_to_support)
    await message.answer(text=text_start_write_message_to_support, parse_mode="html")


@rt.message(StepsTechnicalSupport.start_write_message_to_support)
async def end_send_msg_to_support(message: Message, state: FSMContext, bot_object: Bot):
    await state.clear()
    contacting_msg = f"<b>🆕🗣 Новое обращение</b>\n\n"\
                     f"<b>Полное имя отправителя:</b> {message.from_user.full_name}\n"\
                     f"<b>Ссылка на аккаунт:</b> https://t.me/{message.from_user.username}\n"\
                     f"<b>Содержание:</b> {message.text}"
    await bot_object.send_message(text=contacting_msg, chat_id=TECHNICAL_SUPPORT_GROUP_CHAT_ID,
                                  disable_web_page_preview=True)
    await message.answer(text=text_end_send_msg_to_support)
