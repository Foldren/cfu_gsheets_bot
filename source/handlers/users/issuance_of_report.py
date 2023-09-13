from aiogram import Router, F, Bot
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from components.filters import IsUserFilter
from components.tools import get_callb_content, get_inline_keyb_markup, get_confirm_issuance_keyb_button
from components.users.text_generators import get_msg_notify_new_issuance_of_report
from components.users.texts import text_invalid_volume_operation, text_start_issuance, text_select_worker_issuance, \
    text_set_volume_issuance, text_select_payment_method_issuance, text_no_notify_groups, text_end_issuance, \
    text_select_notify_group_issuance
from config import BANKS_UPRAVLYAIKA
from services.models_extends.issuance_report import IssuanceReportApi
from services.models_extends.menu_item import MenuItemApi
from services.models_extends.notify_group import NotifyGroupApi
from services.models_extends.user import UserApi
from services.redis_extends.user import RedisUser
from states.user.steps_create_notes_to_bd import StepsWriteIssuanceReport

rt = Router()

# Фильтр на проверку категории доступа пользователя
rt.message.filter(IsUserFilter())
rt.callback_query.filter(IsUserFilter())


@rt.message(F.text == "Выдача под отчет")
async def start_write_issuance_of_report_to_bd(message: Message, state: FSMContext, redis_users: RedisUser):
    await state.clear()
    await state.set_state(StepsWriteIssuanceReport.select_ip)

    admin_id = await redis_users.get_user_admin_id(message.from_user.id)
    check_admin_empty_groups = await NotifyGroupApi.check_admin_groups_empty(admin_id)

    if check_admin_empty_groups:
        await message.answer(text=text_no_notify_groups, parse_mode="html")
    else:
        ips = await MenuItemApi.get_user_upper_items(admin_id)

        keyboard = await get_inline_keyb_markup(
            list_names=[ip['name'] for ip in ips],
            list_data=[f"{ip['id']}:{ip['name']}" for ip in ips],
            callback_str="ip_to_issuance",
            number_cols=2
        )

        await state.set_data({
            'admin_id': admin_id,
        })

        await message.answer(text=text_start_issuance, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteIssuanceReport.select_ip, F.data.startswith("ip_to_issuance"))
async def choose_issuance_worker(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteIssuanceReport.select_worker)

    selected_ip_params = await get_callb_content(callback.data, multiply_values=True)

    await state.update_data({
        'selected_ip_id': selected_ip_params[1],
        'selected_ip_name': selected_ip_params[2],
    })

    st_data = await state.get_data()
    ip_workers = await UserApi.get_admin_users(st_data['admin_id'])

    keyboard = await get_inline_keyb_markup(
        list_names=[f"{w['fullname'].split(' ')[1]} - {w['profession']}" for w in ip_workers],
        list_data=[w['chat_id'] for w in ip_workers],
        callback_str="worker_to_issuance",
        number_cols=2
    )

    await callback.message.edit_text(text=text_select_worker_issuance, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteIssuanceReport.select_worker, F.data.startswith("worker_to_issuance"))
async def set_volume_for_issuance(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteIssuanceReport.set_volume)
    selected_worker_id = await get_callb_content(callback.data)
    selected_worker = await UserApi.get_by_id(selected_worker_id)

    await state.update_data({
        'selected_worker_id': selected_worker_id,
        'selected_worker_nickname': selected_worker.nickname
    })

    await callback.message.edit_text(text=text_set_volume_issuance, parse_mode="html")


@rt.message(StepsWriteIssuanceReport.set_volume)
async def select_payment_method_issuance(message: Message, state: FSMContext):
    await state.set_state(StepsWriteIssuanceReport.select_payment_method)

    try:
        volume_op = int(message.text)
    except Exception:
        await state.set_state(StepsWriteIssuanceReport.set_volume)
        await message.answer(text=text_invalid_volume_operation, parse_mode="html")
        return

    await state.update_data({
        'specified_volume': volume_op
    })

    keyboard = await get_inline_keyb_markup(
        list_names=BANKS_UPRAVLYAIKA,
        list_data=BANKS_UPRAVLYAIKA,
        callback_str="select_payment_method_issuance",
        number_cols=2
    )

    await message.answer(text=text_select_payment_method_issuance, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteIssuanceReport.select_payment_method, F.data.startswith("select_payment_method_issuance"))
async def select_group_for_notify(callback: CallbackQuery, state: FSMContext):
    await state.set_state(StepsWriteIssuanceReport.select_notify_group)
    await state.update_data({
        'selected_payment_method': await get_callb_content(callback.data)
    })

    st_data = await state.get_data()
    notify_groups = await UserApi.get_notify_groups(st_data['admin_id'])

    keyboard = await get_inline_keyb_markup(
        list_names=[ng['name'] for ng in notify_groups],
        list_data=[ng['chat_id'] for ng in notify_groups],
        callback_str="select_notify_group_issuance",
        number_cols=2
    )

    await callback.message.edit_text(text=text_select_notify_group_issuance, reply_markup=keyboard, parse_mode="html")


@rt.callback_query(StepsWriteIssuanceReport.select_notify_group, F.data.startswith("select_notify_group_issuance"))
async def end_write_issuance_of_report_to_bd(callback: CallbackQuery, state: FSMContext, bot_object: Bot):
    selected_notify_group_chat_id = int(await get_callb_content(callback.data))
    st_data = await state.get_data()
    user = await UserApi.get_by_id(callback.message.chat.id)

    # Генерируем сообщение уведомления ---------------------------------------------------------------------------------
    msg_in_group = await get_msg_notify_new_issuance_of_report(
        profession_worker=user.profession,
        fullname_worker=user.fullname,
        ip=st_data['selected_ip_name'],
        nickname_second_worker=st_data['selected_worker_nickname'],
        volume=st_data['specified_volume'],
        payment_method=st_data['selected_payment_method']
    )

    # Создаем запись о новой выдаче под отчет в бд ---------------------------------------------------------------------
    issuance_report = await IssuanceReportApi.add_new_issuance_report(
        user_id=callback.message.chat.id,
        org_name=st_data['selected_ip_name'],
        selected_user_nickname=st_data['selected_worker_nickname'],
        selected_user_id=st_data['selected_worker_id'],
        volume=st_data['specified_volume'],
        payment_method=st_data['selected_payment_method'],
        selected_notify_group_id=selected_notify_group_chat_id
    )

    # Отправляем сообщение с подтверждением в группу -------------------------------------------------------------------
    message_notify = await bot_object.send_message(
        chat_id=selected_notify_group_chat_id,
        text=msg_in_group,
        parse_mode="html",
        reply_markup=await get_confirm_issuance_keyb_button(issuance_report.id),
    )

    # Добавляем id сообщения
    issuance_report.message_id = message_notify.message_id
    await issuance_report.save()

    await state.clear()
    await callback.message.edit_text(text=text_end_issuance, parse_mode="html")










