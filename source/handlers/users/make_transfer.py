from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter
from components.tools import get_callb_content, get_inline_keyb_markup, send_multiply_messages
from components.users.text_generators import get_msg_notify_new_transfer
from components.users.texts import text_invalid_volume_operation, text_start_issuance, text_select_wallet_sender, \
    text_end_transfer, text_select_wallet_recipient, \
    text_set_volume_transfer
from config import BANKS_UPRAVLYAIKA
from services.google_api.google_table import GoogleTable
from services.models_extends.menu_item import MenuItemApi
from services.models_extends.notify_group import NotifyGroupApi
from services.models_extends.user import UserApi
from services.redis_extends.user import RedisUser
from states.user.steps_create_notes_to_bd import StepsWriteTransfer

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter())
rt.callback_query.filter(IsUserFilter())


@rt.message(F.text == "Перевод")
async def start_write_transfer_to_bd(message: Message, state: FSMContext, redis_users: RedisUser):
    await state.clear()
    await state.set_state(StepsWriteTransfer.select_organization)

    admin_id = await redis_users.get_user_admin_id(message.from_user.id)
    organizations = await MenuItemApi.get_user_upper_items(admin_id)

    keyboard = await get_inline_keyb_markup(
        list_names=[org['name'] for org in organizations],
        list_data=[org['name'] for org in organizations],
        callback_str="org_to_transfer",
        number_cols=2
    )

    await state.set_data({
        'admin_id': admin_id,
    })

    await message.answer(text=text_start_issuance, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteTransfer.select_organization, F.data.startswith("org_to_transfer"))
async def set_volume_for_issuance(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteTransfer.set_volume)
    selected_org_name = await get_callb_content(callback.data)

    await state.update_data({
        'selected_org_name': selected_org_name,
    })

    await callback.message.edit_text(text=text_set_volume_transfer, parse_mode="html")


@rt.message(StepsWriteTransfer.set_volume)
async def select_wallet_sender(message: Message, state: FSMContext):
    await state.set_state(StepsWriteTransfer.select_wallet_sender)

    try:
        volume_op = int(message.text)
    except Exception:
        await state.set_state(StepsWriteTransfer.set_volume)
        await message.answer(text=text_invalid_volume_operation, parse_mode="html")
        return

    await state.update_data({
        'specified_volume': volume_op
    })

    keyboard = await get_inline_keyb_markup(
        list_names=BANKS_UPRAVLYAIKA,
        list_data=BANKS_UPRAVLYAIKA,
        callback_str="select_wallet_sender",
        number_cols=2
    )

    await message.answer(text=text_select_wallet_sender, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteTransfer.select_wallet_sender, F.data.startswith("select_wallet_sender"))
async def select_wallet_recipient(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteTransfer.select_wallet_recipient)

    await state.update_data({
        'wallet_sender': await get_callb_content(callback.data)
    })

    keyboard = await get_inline_keyb_markup(
        list_names=BANKS_UPRAVLYAIKA,
        list_data=BANKS_UPRAVLYAIKA,
        callback_str="select_wallet_recipient",
        number_cols=2
    )

    await callback.message.edit_text(text=text_select_wallet_recipient, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteTransfer.select_wallet_recipient, F.data.startswith("select_wallet_recipient"))
async def end_write_transfer_to_bd(callback: CallbackQuery, state: FSMContext,
                                   bot_object: Bot, gt_object: GoogleTable):
    wallet_recipient = await get_callb_content(callback.data)
    st_data = await state.get_data()
    user = await UserApi.get_by_id(callback.message.chat.id)
    table_url = await UserApi.get_table_url(st_data['admin_id'])

    # Вносим в google таблицу запись -----------------------------------------------------------------------------------
    await callback.message.edit_text(
        text='Добавляю запись в вашу гугл таблицу 🔄 \n\n🟩🟩🟩◻◻◻◻◻◻◻',
        parse_mode="html"
    )

    await gt_object.add_transfer_to_bd(
        table_url=table_url,
        chat_id_worker=callback.message.chat.id,
        volume_op=st_data['specified_volume'],
        wallet_sender=st_data['wallet_sender'],
        wallet_recipient=wallet_recipient,
        org_name=st_data['selected_org_name']
    )

    empty_notify_groups_flag = await NotifyGroupApi.check_admin_groups_empty(st_data['admin_id'])

    # Отправляем уведомление -------------------------------------------------------------------------------------------
    await callback.message.edit_text(
        text='Проверяю включен ли я в ваши группы 🧐 \n\n🟩🟩🟩🟩🟩🟩◻◻◻◻',
        parse_mode="html"
    )

    if not empty_notify_groups_flag:
        await callback.message.edit_text(
            text='Включен, отправляю уведомления в группы 📩 \n\n🟩🟩🟩🟩🟩🟩🟩🟩🟩🟩',
            parse_mode="html"
        )

        msg_in_group = await get_msg_notify_new_transfer(
            profession_worker=user.profession,
            fullname_worker=user.fullname,
            organization=st_data['selected_org_name'],
            wallet_sender=st_data['wallet_sender'],
            wallet_recipient=wallet_recipient,
            volume=st_data['specified_volume']
        )

        list_notify_groups_chat_ids = await NotifyGroupApi.get_admin_notify_groups_chat_ids(st_data['admin_id'])

        # Отправляем уведомление в группы ------------------------------------------------------------------------------
        await send_multiply_messages(
            bot=bot_object,
            msg_text=msg_in_group,
            list_chat_ids=list_notify_groups_chat_ids
        )

    await state.clear()
    await callback.message.edit_text(text=text_end_transfer, parse_mode="html")
